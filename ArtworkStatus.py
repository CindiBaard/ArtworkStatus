import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
CSV_FILE = 'Artwork Status.csv'
BACKUP_FILE = 'Artwork_Status_Backup.csv'
REF_FILE = 'https://docs.google.com/spreadsheets/d/1TiuVzyZLbLAFQ_Os8mzwURFaFV3GJNklBY13PCajkmA/gviz/tq?tqx=out:csv'

# --- HELPER FUNCTIONS ---
def format_date(date_val):
    if date_val:
        return date_val.strftime('%d.%m.%Y')
    return ""

def parse_date(date_str):
    if not date_str or pd.isna(date_str) or date_str == "":
        return None
    try:
        return datetime.strptime(str(date_str).strip(), '%d.%m.%Y').date()
    except:
        return None

def clean_val(val):
    if pd.isna(val): return ""
    s = str(val).strip().replace(',', '')
    if s.endswith('.0'): s = s[:-2]
    return s

def main():
    st.set_page_config(page_title="Artwork Status Portal", layout="wide")
    st.title("🎨 Artwork Status Entry Form")

    # --- SESSION STATE ---
    form_fields = [
        "found_client", "found_desc", "found_req", "found_status", 
        "found_comments", "found_date_rec", "found_date_wtsp", "found_date_client",
        "found_date_appr", "found_date_plates", "found_date_arr", "found_date_foil",
        "found_date_farr", "found_quoted", "found_spec"
    ]
    for field in form_fields:
        if field not in st.session_state:
            st.session_state[field] = "" if "date" not in field else None

    # --- STEP 1: LOOKUP ---
    st.subheader("Step 1: Project Lookup")
    col1, col2 = st.columns([1, 2])
    with col1:
        search_no = st.text_input("Enter Pre-Prod No.", placeholder="e.g. 12326")
    
    if st.button("Search Tracker"):
        if not search_no:
            st.warning("Please enter a number.")
        else:
            try:
                target = clean_val(search_no)
                df_ref = pd.read_csv(REF_FILE, encoding='utf-8-sig')
                df_ref.columns = [str(c).strip() for c in df_ref.columns]
                id_col = next((c for c in df_ref.columns if "pre" in c.lower() and "no" in c.lower()), "Pre-Prod No.")
                df_ref[id_col] = df_ref[id_col].apply(clean_val)
                ref_match = df_ref[df_ref[id_col] == target]
                
                if not ref_match.empty:
                    client_col = next((c for c in df_ref.columns if "client" in c.lower()), "Client")
                    desc_col = next((c for c in df_ref.columns if "project" in c.lower() and "desc" in c.lower()), "Project Description")
                    st.session_state.found_client = clean_val(ref_match.iloc[0].get(client_col, ''))
                    st.session_state.found_desc = clean_val(ref_match.iloc[0].get(desc_col, ''))
                    
                    if os.path.exists(CSV_FILE):
                        try:
                            df_local = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8-sig')
                        except:
                            df_local = pd.read_csv(CSV_FILE, sep=';', encoding='latin1')
                        
                        df_local['Pre-Prod No.'] = df_local['Pre-Prod No.'].apply(clean_val)
                        local_match = df_local[df_local['Pre-Prod No.'] == target]
                        
                        if not local_match.empty:
                            row = local_match.iloc[-1]
                            st.session_state.found_req = row.get("Artwork required", "")
                            st.session_state.found_status = row.get("STATUS", "")
                            st.session_state.found_comments = row.get("Comments", "")
                            st.session_state.found_spec = row.get("Spec Supplied", "")
                            st.session_state.found_date_rec = parse_date(row.get("Artwork Received"))
                            st.session_state.found_date_wtsp = parse_date(row.get("Sent Proof for WT_SP"))
                            st.session_state.found_date_client = parse_date(row.get("Sent Proof to Client"))
                            st.session_state.found_date_appr = parse_date(row.get("Proof Approved (Conventional)"))
                            st.session_state.found_date_plates = parse_date(row.get("Ordered Plates"))
                            st.session_state.found_date_arr = parse_date(row.get("Plates Arrived"))
                            st.session_state.found_date_foil = parse_date(row.get("Ordered Foil Block"))
                            st.session_state.found_date_farr = parse_date(row.get("Foil Block Arrived"))
                            st.session_state.found_quoted = parse_date(row.get("Quoted"))
                            st.info("💡 Pulled existing progress from local database.")
                    st.success(f"✅ Found: {st.session_state.found_client}")
                else:
                    st.error("ID not found in Google Sheets.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # --- STEP 2: FORM ---
    st.subheader("Step 2: Complete Record Information")
    with st.form("main_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            client = st.text_input("Client", value=st.session_state.found_client)
            proj_desc = st.text_input("Project Description", value=st.session_state.found_desc)
            artwork_req = st.selectbox("Artwork Required", ["", "X"], index=1 if st.session_state.found_req == "X" else 0)
            status = st.text_input("Status", value=st.session_state.found_status)
            comments = st.text_area("Comments", value=st.session_state.found_comments)
            date_rec = st.date_input("Artwork Received", value=st.session_state.found_date_rec, format="DD/MM/YYYY")
            date_wtsp = st.date_input("Sent Proof for WT_SP", value=st.session_state.found_date_wtsp, format="DD/MM/YYYY")
        with right:
            date_client = st.date_input("Sent Proof to Client", value=st.session_state.found_date_client, format="DD/MM/YYYY")
            date_appr = st.date_input("Proof Approved", value=st.session_state.found_date_appr, format="DD/MM/YYYY")
            date_plates = st.date_input("Ordered Plates", value=st.session_state.found_date_plates, format="DD/MM/YYYY")
            date_arr = st.date_input("Plates Arrived", value=st.session_state.found_date_arr, format="DD/MM/YYYY")
            date_foil = st.date_input("Ordered Foil Block", value=st.session_state.found_date_foil, format="DD/MM/YYYY")
            date_farr = st.date_input("Foil Block Arrived", value=st.session_state.found_date_farr, format="DD/MM/YYYY")
            quoted = st.date_input("Quoted", value=st.session_state.found_quoted, format="DD/MM/YYYY")
            spec = st.selectbox("Spec Supplied", ["", "X"], index=1 if st.session_state.found_spec == "X" else 0)

        if st.form_submit_button("Upload Information"):
            if not search_no:
                st.error("Please enter an ID first.")
            else:
                new_row = {
                    "Pre-Prod No.": search_no, "Client": client, "Project Description": proj_desc,
                    "Artwork required": artwork_req, "STATUS": status, "Comments": comments,
                    "Artwork Received": format_date(date_rec), "Sent Proof for WT_SP": format_date(date_wtsp),
                    "Sent Proof to Client": format_date(date_client), "Proof Approved (Conventional)": format_date(date_appr),
                    "Ordered Plates": format_date(date_plates), "Plates Arrived": format_date(date_arr),
                    "Ordered Foil Block": format_date(date_foil), "Foil Block Arrived": format_date(date_farr),
                    "Quoted": format_date(quoted), "Spec Supplied": spec
                }
                try:
                    df_to_save = pd.DataFrame([new_row])
                    df_to_save.to_csv(CSV_FILE, mode='a', index=False, header=not os.path.exists(CSV_FILE), sep=';', encoding='utf-8-sig')
                    df_to_save.to_csv(BACKUP_FILE, mode='a', index=False, header=not os.path.exists(BACKUP_FILE), sep=';', encoding='utf-8-sig')
                    st.success("🎉 Updated database and created backup!")
                    for field in form_fields: st.session_state[field] = "" if "date" not in field else None
                except Exception as e:
                    st.error(f"Save Error: {e}")

    # --- STEP 3: TOOLS ---
    st.divider()
    st.subheader("Step 3: Database Tools")
    if st.button("🔍 View/Download Database"):
        if os.path.exists(CSV_FILE):
            try:
                try: df_view = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8-sig')
                except: df_view = pd.read_csv(CSV_FILE, sep=';', encoding='latin1')
                st.dataframe(df_view, use_container_width=True)
                csv_data = df_view.to_csv(index=False, sep=';').encode('utf-8-sig')
                st.download_button("📥 Download CSV", data=csv_data, file_name="Artwork_Status.csv", mime="text/csv")
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("No database found.")

    with st.expander("⚠️ Danger Zone - Delete a Record"):
        st.write("This will permanently remove the record from the main database.")
        del_id = st.text_input("Enter ID to Delete", key="del_id_input")
        confirm_check = st.checkbox("I confirm I want to delete this record.")
        verify_text = st.text_input("Type 'DELETE' to confirm", key="verify_input")
        
        if st.button("Permanently Delete", type="primary"):
            if del_id and confirm_check and verify_text == "DELETE":
                if os.path.exists(CSV_FILE):
                    try:
                        try: df_del = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8-sig')
                        except: df_del = pd.read_csv(CSV_FILE, sep=';', encoding='latin1')
                        df_del['Pre-Prod No.'] = df_del['Pre-Prod No.'].apply(clean_val)
                        if clean_val(del_id) in df_del['Pre-Prod No.'].values:
                            df_updated = df_del[df_del['Pre-Prod No.'] != clean_val(del_id)]
                            df_updated.to_csv(CSV_FILE, index=False, sep=';', encoding='utf-8-sig')
                            st.success(f"Deleted ID {del_id}!")
                            st.rerun()
                        else: st.error("ID not found.")
                    except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Please complete all 3 security steps.")

if __name__ == "__main__":
    main()
    # Create a backup copy every time you save
df_to_save.to_csv("Artwork_Status_Backup.csv", mode='a', index=False, sep=';', header=not os.path.exists("Artwork_Status_Backup.csv"))