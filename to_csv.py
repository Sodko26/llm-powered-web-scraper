import csv
import json

def _format_nested_data(nested_list):
    """
    Formats a list of dictionaries (like qualifications or courses) into a single,
    human-readable, multi-line string for a CSV cell.
    """
    if not nested_list:
        return ""
    
    formatted_lines = []
    for item in nested_list:
        # Creates a line like: "Code: BSB30120, Title: Certificate III in Business, Status: Current"
        details = [
            f"Code: {item.get('Code', 'N/A')}",
            f"Title: {item.get('Title', 'N/A')}",
            f"Status: {item.get('Status', 'N/A')}",
            f"Start Date: {item.get('Start Date', 'N/A')}",
            f"End Date: {item.get('End Date', 'N/A')}"
        ]
        formatted_lines.append(", ".join(details))
    
    # Joins each item with a newline character. Excel will treat this as a multi-line cell.
    return "\n".join(formatted_lines)

def convert_rto_json_to_csv(list_of_rto_data, output_csv_path):
    """
    Reads a list of RTO JSON objects, processes them, and writes to a CSV file.

    Args:
        list_of_rto_data (list): A list of dictionaries, where each dictionary is an RTO record.
        output_csv_path (str): The file path for the output CSV file.
    """
    # Predefined headers based on the top-level keys in your JSON object.
    headers = [
        "Code", "Legal Name", "Business Name", "Status", "ABN", "ACN", 
        "RTO Type", "Web Address", "Registration Manager", "Initial Registration Date",
        "Start Date", "End Date", "Legal Authority", "Chief Executive Contact Name",
        "Chief Executive Title", "Chief Executive Phone", "Chief Executive Email",
        "Registration Enquiries Contact Name", "Registration Enquiries Title",
        "Registration Enquiries Phone", "Registration Enquiries Email",
        "Public Enquiries Contact Name", "Public Enquiries Title",
        "Public Enquiries Phone", "Public Enquiries Email", "Address",
        "Qualifications", "Courses"
    ]

    print(f"Writing data to {output_csv_path}...")

    try:
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)

            # Write the header row first
            writer.writerow(headers)

            # Process and write each RTO record
            for rto_record in list_of_rto_data:
                row = []
                for header in headers:
                    if header == "Qualifications":
                        # Format the nested qualifications list into a single string
                        row.append(_format_nested_data(rto_record.get("Qualifications")))
                    elif header == "Courses":
                        # Format the nested courses list into a single string
                        row.append(_format_nested_data(rto_record.get("Courses")))
                    else:
                        # Get the value for other top-level fields, default to empty string if not found
                        row.append(rto_record.get(header, ""))
                
                writer.writerow(row)
        
        print("✅ Successfully created CSV file.")

    except IOError as e:
        print(f"❌ Error writing to file: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    # Your sample JSON object provided in the prompt
    sample_rto_data = [
        {
            "Code": "0049",
            "Legal Name": "Australian Institute of Management Education and Training Pty Ltd",
            "Business Name": "AIM VET",
            "Status": "Current",
            "ABN": "40009668553",
            "ACN": "009668553",
            "RTO Type": "Education/training Business Or Centre: Privately Operated Registered Training Organisation",
            "Web Address": "http://aim.com.au/",
            "Registration Manager": None,
            "Initial Registration Date": "01/Jan/1998",
            "Start Date": "31/Dec/2023",
            "End Date": "31/Dec/2030",
            "Legal Authority": "National Vocational Education and Training Regulator Act 2011",
            "Chief Executive Contact Name": "Mr. Martin Mercer",
            "Chief Executive Title": "CEO",
            "Chief Executive Phone": "0475030068",
            "Chief Executive Email": "martin.mercer@aim.com.au",
            "Registration Enquiries Contact Name": "Ms. Aliki Voukelatos",
            "Registration Enquiries Title": "Senior Policy and Compliance Officer",
            "Registration Enquiries Phone": "0410841995",
            "Registration Enquiries Email": "avoukelatos@scentia.com.au",
            "Public Enquiries Contact Name": "Student Services",
            "Public Enquiries Title": None,
            "Public Enquiries Phone": "1300658337",
            "Public Enquiries Email": "studentsupport@aim.com.au",
            "Address": "Ground Floor 7-15 Macquarie Pl, SYDNEY, NSW, 2000",
            "Qualifications": [
                {
                    "Code": "BSB30120",
                    "Title": "Certificate III in Business",
                    "Status": "Current",
                    "Start Date": "26/Nov/2024",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB40120",
                    "Title": "Certificate IV in Business",
                    "Status": "Current",
                    "Start Date": "24/May/2025",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB40420",
                    "Title": "Certificate IV in Human Resource Management",
                    "Status": "Current",
                    "Start Date": "17/Dec/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB40520",
                    "Title": "Certificate IV in Leadership and Management",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB40920",
                    "Title": "Certificate IV in Project Management Practice",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB41419",
                    "Title": "Certificate IV in Work Health and Safety",
                    "Status": "Current",
                    "Start Date": "30/Aug/2019",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB50120",
                    "Title": "Diploma of Business",
                    "Status": "Current",
                    "Start Date": "17/Dec/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB50320",
                    "Title": "Diploma of Human Resource Management",
                    "Status": "Current",
                    "Start Date": "17/Dec/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB50420",
                    "Title": "Diploma of Leadership and Management",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB50820",
                    "Title": "Diploma of Project Management",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB60320",
                    "Title": "Advanced Diploma of Finance and Mortgage Broking Management",
                    "Status": "Current",
                    "Start Date": "26/Nov/2024",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB60420",
                    "Title": "Advanced Diploma of Leadership and Management",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB60620",
                    "Title": "Advanced Diploma of Work Health and Safety",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "BSB60720",
                    "Title": "Advanced Diploma of Program Management",
                    "Status": "Current",
                    "Start Date": "19/Oct/2020",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "MSS40322",
                    "Title": "Certificate IV in Competitive Systems and Practices",
                    "Status": "Current",
                    "Start Date": "26/Nov/2024",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                }
            ],
            "Courses": [
                {
                    "Code": "10787NAT",
                    "Title": "Advanced Diploma of Digital Marketing",
                    "Status": "Non-current",
                    "Start Date": "09/Dec/2021",
                    "End Date": "21/May/2026",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "10904NAT",
                    "Title": "Diploma of Social Media Marketing",
                    "Status": "Current",
                    "Start Date": "17/Dec/2020",
                    "End Date": "14/Mar/2028",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "10931NAT",
                    "Title": "Diploma of Digital Marketing",
                    "Status": "Current",
                    "Start Date": "09/Dec/2021",
                    "End Date": "24/Mar/2028",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "11287NAT",
                    "Title": "Diploma of Artificial Intelligence (AI)",
                    "Status": "Current",
                    "Start Date": "26/Nov/2024",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                },
                {
                    "Code": "11291NAT",
                    "Title": "Diploma of Professional Coaching",
                    "Status": "Current",
                    "Start Date": "26/Nov/2024",
                    "End Date": "31/Dec/2030",
                    "Delivery Notification": ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT", "INTERNATIONAL"]
                }
            ]
        },
        {
            "Code": "0115",
            "Legal Name": "Australian Institute of Management Education and Training Pty Ltd",
            "Business Name": "AIM VET",
            "Status": "Current",
            "ABN": "40009668553",
            "ACN": "009668553",
            "RTO Type": "Education/training Business Or Centre: Privately Operated Registered Training Organisation",
            "Web Address": "http://aim.com.au/",
            "Registration Manager": None,
            "Initial Registration Date": "01/Jan/1998",
            "Start Date": "31/Dec/2023",
            "End Date": "31/Dec/2030",
            "Legal Authority": "National Vocational Education and Training Regulator Act 2011",
            "Chief Executive Contact Name": "Mr. Martin Mercer",
            "Chief Executive Title": "CEO",
            "Chief Executive Phone": "0475030068",
            "Chief Executive Email": "martin.mercer@aim.com.au",
            "Registration Enquiries Contact Name": "Ms. Aliki Voukelatos",
            "Registration Enquiries Title": "Senior Policy and Compliance Officer",
            "Registration Enquiries Phone": "0410841995",
            "Registration Enquiries Email": "avoukelatos@scentia.com.au",
            "Public Enquiries Contact Name": "Student Services",
            "Public Enquiries Title": None,
            "Public Enquiries Phone": "1300658337",
            "Public Enquiries Email": "studentsupport@aim.com.au",
            "Address": "Ground Floor 7-15 Macquarie Pl, SYDNEY, NSW, 2000",
            "Qualifications": [
                {"Code": "BSB30120", "Title": "Certificate III in Business", "Status": "Current", "Start Date": "26/Nov/2024", "End Date": "31/Dec/2030"},
                {"Code": "BSB40120", "Title": "Certificate IV in Business", "Status": "Current", "Start Date": "24/May/2025", "End Date": "31/Dec/2030"},
            ],
            "Courses": [
                {"Code": "10787NAT", "Title": "Advanced Diploma of Digital Marketing", "Status": "Non-current", "Start Date": "09/Dec/2021", "End Date": "21/May/2026"},
                {"Code": "10904NAT", "Title": "Diploma of Social Media Marketing", "Status": "Current", "Start Date": "17/Dec/2020", "End Date": "14/Mar/2028"},
            ]
        }
        # You can add more RTO JSON objects to this list
    ]
    
    output_filename = 'rto_output.csv'
    
    # Call the function with your data
    convert_rto_json_to_csv(sample_rto_data, output_filename)