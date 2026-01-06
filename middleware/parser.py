from datetime import datetime

def parse_frame(frame):
    """
    Parses an ASTM bytes frame and returns dictionaries for Patient, Order, and Results.
    """
    # 1. Decode bytes to string
    message = frame.decode(errors='ignore')
    
    # 2. CRITICAL FIX: Normalize Line Endings
    # Convert \n (Simulator) to \r (Standard) so we can split correctly
    message = message.replace('\n', '\r')
    
    # 3. Split into lines
    lines = [line for line in message.split('\r') if line.strip()]
    
    patient = {}
    order = {}
    results = []

    for line in lines:
        parts = line.split('|')
        
        # --- PATIENT RECORD (P) ---
        if line.startswith('P|'):
            # Data: P|1|||adhikari^ram||...
            # Indices: 0 1 2 3 4
            
            # 1. Extract Name
            # Your data has name at index 4 (Standard is 5). We check both.
            name_raw = ""
            if len(parts) > 5 and '^' in parts[5]:
                name_raw = parts[5]
            elif len(parts) > 4 and '^' in parts[4]:
                name_raw = parts[4]
            
            # Clean up name (Remove ^)
            name_parts = name_raw.split('^') if name_raw else []
            patient['patient_name'] = ' '.join([p for p in name_parts if p.strip()])
            
            # 2. Extract ID
            # Check indices 2, 3, 4. If empty, use "Unknown"
            id_val = ""
            for i in [2, 3, 4]:
                if len(parts) > i and parts[i].strip() and '^' not in parts[i]:
                    id_val = parts[i].strip()
                    break
            patient['patient_id'] = id_val or "unknown"

            # 3. Gender
            for i in [8, 7, 9]:
                if len(parts) > i and parts[i].strip() in ['M', 'F']:
                    patient['gender'] = parts[i].strip()
                    break

        # --- ORDER RECORD (O) ---
        elif line.startswith('O|'):
            # O|1|BC-692195||...
            # Barcode is at Index 2
            raw_id = parts[2].strip() if len(parts) > 2 else ""
            order['order_id'] = raw_id.split('^')[0]
            order['placer_order'] = order['order_id']
            
            # Sample Type
            raw_sample = parts[15].strip() if len(parts) > 15 else ""
            order['sample_type'] = raw_sample.split('^')[0]

        # --- RESULT RECORD (R) ---
        elif line.startswith('R|'):
            # R|1|^^^WBC|8.5|...
            
            # Test Code (Index 2)
            test_raw = parts[2].split('^') if len(parts) > 2 else []
            test_code = next((x for x in test_raw if x.strip()), "Unknown")

            # Value (Index 3)
            result_val = parts[3].strip() if len(parts) > 3 else ""
            
            # Unit (Index 4)
            unit_val = parts[4].strip() if len(parts) > 4 else ""
            
            # Range (Index 5)
            range_val = parts[5].strip() if len(parts) > 5 else ""
            
            # Flags (Index 6)
            flag_raw = parts[6].strip() if len(parts) > 6 else ""
            abnormal_flag = flag_raw.replace('\\', ' ') if flag_raw else ""

            results.append({
                'test_code': test_code,
                'result_value': result_val,
                'unit': unit_val,
                'ref_range': range_val,
                'abnormal_flag': abnormal_flag
            })

    return patient, order, results