from datetime import datetime

def parse_frame(frame):
    """
    Parses an ASTM bytes frame and returns dictionaries for Patient, Order, and Results.
    """
    message = frame.decode(errors='ignore')
    lines = message.split('\r')
    
    patient = {}
    order = {}
    results = []

    for line in lines:
        parts = line.split('|')
        
        # --- PATIENT RECORD (P) ---
        if line.startswith('P|'):
            # Example: P|1|12345|||Doe^John|||...
            patient['patient_id'] = parts[2].strip() if len(parts) > 2 else "unknown"
            
            # Handle Name (Last^First^Middle)
            name_parts = parts[5].split('^') if len(parts) > 5 else []
            # Join non-empty parts with space
            patient['patient_name'] = ' '.join([p for p in name_parts if p.strip()])
            
            # Gender
            gender_raw = parts[8].strip() if len(parts) > 8 else None
            patient['gender'] = gender_raw[0] if gender_raw else None

        # --- ORDER RECORD (O) ---
        elif line.startswith('O|'):
            # Example: O|1|Barcode123||...
            raw_id = parts[2].strip() if len(parts) > 2 else ""
            # Some machines send ID^Issuer^Type
            order['order_id'] = raw_id.split('^')[0] if '^' in raw_id else raw_id
            order['placer_order'] = order['order_id']
            
            # Sample Type
            raw_sample = parts[15].strip() if len(parts) > 15 else ""
            order['sample_type'] = raw_sample.split('^')[0]

        # --- RESULT RECORD (R) ---
        elif line.startswith('R|'):
            # Example: R|1|^^^WBC|10.5|...
            
            # Extract Test Code (Usually ^^^Code)
            test_raw = parts[2].split('^') if len(parts) > 2 else []
            test_code = next((x for x in test_raw if x.strip()), "Unknown")

            # Extract Flags (High/Low)
            # Flags are often in index 6, but sometimes split by \
            flag_raw = parts[6].strip() if len(parts) > 6 else ""
            abnormal_flag = flag_raw.replace('\\', ' ') if flag_raw else "NORMAL"

            results.append({
                'test_code': test_code,
                'result_value': parts[3].strip() if len(parts) > 3 else "",
                'unit': parts[4].strip() if len(parts) > 4 else "",
                'ref_range': parts[5].strip() if len(parts) > 5 else "",
                'abnormal_flag': abnormal_flag
            })

    return patient, order, results