import requests
import json
from datetime import datetime
from colorama import Fore, Style, init

init()

def format_date(date_str):
   if date_str:
       dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
       return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
   return 'N/A'

def format_currency(amount):
   return f"{Fore.YELLOW}${amount:,.2f}{Style.RESET_ALL}"

def get_color(index):
   colors = [Fore.BLUE, Fore.GREEN, Fore.MAGENTA, Fore.CYAN, Fore.RED]
   return colors[index % len(colors)]

def fetch_data():
   base_url = "https://api.usaspending.gov"
   awards_count_url = f"{base_url}/api/v2/agency/015/awards/new/count/"
   agencies_url = f"{base_url}/api/v2/reporting/agencies/overview/"
   federal_account_url = f"{base_url}/api/v2/agency/015/federal_account/"
   
   try:
       print("\n=== DOJ NEW AWARDS COUNT ===\n")
       response = requests.get(awards_count_url)
       if response.status_code == 200:
           count_data = response.json()
           print("NEW AWARDS BREAKDOWN")
           if isinstance(count_data, dict):
               for award_type, count in count_data.items():
                   award_type_formatted = award_type.replace('_', ' ').title()
                   print(f"{award_type_formatted}: {count}")
               total = sum(count for count in count_data.values() if isinstance(count, (int, float)))
               print(f"\nTotal New Awards: {total}")
       else:
           print(f"Error fetching awards count. Status code: {response.status_code}")

       print("\n=== DOJ FEDERAL ACCOUNTS ===")
       response = requests.get(federal_account_url)
       if response.status_code == 200:
           account_data = response.json()
           
           page_metadata = account_data.get('page_metadata', {})
           print(f"\nTotal Federal Accounts: {page_metadata.get('total')}")
           print(f"Page: {page_metadata.get('page')} of {page_metadata.get('total')}")
           print(f"Results per page: {page_metadata.get('limit')}\n")
           
           for idx, account in enumerate(account_data.get('results', [])):
               print("-"*50)
               color = get_color(idx)
               print(f"{color}Account: {account.get('name')}{Style.RESET_ALL}")
               print(f"Code: {account.get('code')}")
               print("\nChildren Accounts:")
               
               for child in account.get('children', []):
                   print("\n  " + "-"*48)
                   print(f"  {color}Name: {child.get('name')}{Style.RESET_ALL}")
                   print(f"  Code: {child.get('code')}")
                   print(f"  Obligated Amount: {format_currency(child.get('obligated_amount', 0))}")
                   print(f"  Gross Outlay Amount: {format_currency(child.get('gross_outlay_amount', 0))}")
               
               print("\nAccount Totals:")
               print(f"Total Obligated Amount: {format_currency(account.get('obligated_amount', 0))}")
               print(f"Total Gross Outlay Amount: {format_currency(account.get('gross_outlay_amount', 0))}")
               print("-"*50 + "\n")

       print("\n=== AGENCIES OVERVIEW ===")
       response = requests.get(agencies_url)
       if response.status_code == 200:
           data = response.json()
           
           page_metadata = data.get('page_metadata', {})
           print("\n=== PAGINATION INFO ===")
           print(f"Page: {page_metadata.get('page')}")
           print(f"Total Agencies: {page_metadata.get('total')}")
           print(f"Results per page: {page_metadata.get('limit')}")
           
           for agency in data.get('results', []):
               print("\n" + "="*50)
               print(f"{Fore.BLUE}AGENCY: {agency.get('agency_name')} ({agency.get('abbreviation')}){Style.RESET_ALL}")
               print("-"*50)
               print(f"Agency Code: {agency.get('toptier_code')}")
               print(f"Agency ID: {agency.get('agency_id')}")
               print(f"Budget Authority: {format_currency(agency.get('current_total_budget_authority_amount', 0))}")
               
               print(f"\nPublication Date: {Fore.GREEN}{format_date(agency.get('recent_publication_date'))}{Style.RESET_ALL}")
               print(f"Certified: {'Yes' if agency.get('recent_publication_date_certified') else 'No'}")
               
               tas_info = agency.get('tas_account_discrepancies_totals', {})
               print("\nTAS ACCOUNT INFORMATION:")
               print(f"GTAS Obligation Total: {format_currency(tas_info.get('gtas_obligation_total', 0))}")
               print(f"TAS Accounts Total: {format_currency(tas_info.get('tas_accounts_total', 0))}")
               print(f"Missing TAS Accounts: {tas_info.get('missing_tas_accounts_count', 0)}")
               
               print("\nAWARD INFORMATION:")
               print(f"Unlinked Contract Awards: {agency.get('unlinked_contract_award_count', 0):,}")
               print(f"Unlinked Assistance Awards: {agency.get('unlinked_assistance_award_count', 0):,}")
               print(f"Obligation Difference: {format_currency(agency.get('obligation_difference', 0))}")

   except Exception as e:
       print(f"Error: {e}")

if __name__ == "__main__":
   fetch_data()
