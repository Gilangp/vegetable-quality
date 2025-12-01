"""
Master Seeder - Jalankan semua seeder
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.seeders.houses import houses
from database.seeders.families import families
from database.seeders.residents import residents
from database.seeders.users import users
from database.seeders.activity_logs import activity_logs
from database.seeders.resident_approvals import resident_approvals
from database.seeders.family_mutations import family_mutations
from database.seeders.resident_messages import resident_messages
from database.seeders.activities import activities
from database.seeders.broadcasts import broadcasts
from database.seeders.income_categories import income_categories
from database.seeders.income_bills import income_bills
from database.seeders.income_other import income_other
from database.seeders.incomes import incomes
from database.seeders.spendings import spendings
from database.seeders.channels import channels
from database.seeders.verification_results import verification_results
from database.seeders.marketplace_products import marketplace_products
from database.seeders.marketplace_orders import marketplace_orders
from database.seeders.settings import settings

def run_all_seeders():
    """Run all seeders in the correct order based on foreign key dependencies"""
    
    print("\n" + "="*50)
    print("🌱 Starting Database Seeding...")
    print("="*50 + "\n")
    
    # Basic tables (no dependencies)
    print("Step 1: Seeding basic tables...")
    houses()
    income_categories()
    channels()
    settings()
    activities()
    
    # Tables with dependencies
    print("\nStep 2: Seeding population system...")
    families()
    residents()
    
    print("\nStep 3: Seeding user & auth system...")
    users()
    activity_logs()
    resident_approvals()
    
    print("\nStep 4: Seeding resident system...")
    family_mutations()
    resident_messages()
    broadcasts()
    
    print("\nStep 5: Seeding financial system...")
    income_bills()
    income_other()
    incomes()
    spendings()
    
    print("\nStep 6: Seeding PCVK & marketplace...")
    verification_results()
    marketplace_products()
    marketplace_orders()
    
    print("\n" + "="*50)
    print("✅ Database seeding completed successfully!")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        run_all_seeders()
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        sys.exit(1)
