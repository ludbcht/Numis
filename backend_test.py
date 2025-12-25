import requests
import sys
import json
from datetime import datetime

class CoinCollectorAPITester:
    def __init__(self, base_url="https://coin-collector-37.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test login functionality"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        # Test valid login
        success, response = self.run_test(
            "Valid Login (Ludivine/Ludivine67)",
            "POST",
            "auth/login",
            200,
            data={"username": "Ludivine", "password": "Ludivine67"}
        )
        
        if success and response.get('success') and response.get('user'):
            self.user_id = response['user']['id']
            print(f"   User ID: {self.user_id}")
        else:
            print("   ❌ Failed to get user ID from login response")
            return False
            
        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST", 
            "auth/login",
            200,  # API returns 200 with success=false
            data={"username": "wrong", "password": "wrong"}
        )
        
        return True

    def test_coins_api(self):
        """Test coins catalog API"""
        print("\n=== TESTING COINS API ===")
        
        # Get all coins
        success, coins = self.run_test(
            "Get All Coins",
            "GET",
            "coins",
            200
        )
        
        if success and isinstance(coins, list) and len(coins) > 0:
            print(f"   Found {len(coins)} coins")
            self.sample_coin_id = coins[0]['id']
            print(f"   Sample coin ID: {self.sample_coin_id}")
        else:
            print("   ❌ No coins found or invalid response")
            return False
            
        # Get specific coin
        if hasattr(self, 'sample_coin_id'):
            self.run_test(
                "Get Specific Coin",
                "GET",
                f"coins/{self.sample_coin_id}",
                200
            )
        
        # Test filtering by country
        self.run_test(
            "Filter by Country (France)",
            "GET",
            "coins",
            200,
            params={"country": "France"}
        )
        
        # Test filtering by year
        self.run_test(
            "Filter by Year (2024)",
            "GET",
            "coins",
            200,
            params={"year": 2024}
        )
        
        # Test search
        self.run_test(
            "Search Coins (Pasteur)",
            "GET",
            "coins",
            200,
            params={"search": "Pasteur"}
        )
        
        return True

    def test_countries_and_years(self):
        """Test countries and years endpoints"""
        print("\n=== TESTING COUNTRIES AND YEARS ===")
        
        success, countries = self.run_test(
            "Get Countries",
            "GET",
            "countries",
            200
        )
        
        if success and isinstance(countries, list):
            print(f"   Found {len(countries)} countries")
        
        success, years = self.run_test(
            "Get Years",
            "GET",
            "years",
            200
        )
        
        if success and isinstance(years, list):
            print(f"   Found {len(years)} years")
        
        return True

    def test_collection_api(self):
        """Test collection management API"""
        print("\n=== TESTING COLLECTION API ===")
        
        if not self.user_id:
            print("❌ No user ID available for collection tests")
            return False
            
        if not hasattr(self, 'sample_coin_id'):
            print("❌ No sample coin ID available for collection tests")
            return False
        
        # Get empty collection
        self.run_test(
            "Get Collection (Initially Empty)",
            "GET",
            "collection",
            200,
            params={"user_id": self.user_id}
        )
        
        # Add coin to collection
        success, response = self.run_test(
            "Add Coin to Collection",
            "POST",
            "collection/add",
            200,
            data={"coin_id": self.sample_coin_id, "condition": "FDC"},
            params={"user_id": self.user_id}
        )
        
        # Get collection with coin
        success, collection = self.run_test(
            "Get Collection (With Coin)",
            "GET",
            "collection",
            200,
            params={"user_id": self.user_id}
        )
        
        collection_item_id = None
        if success and isinstance(collection, list) and len(collection) > 0:
            collection_item_id = collection[0]['id']
            print(f"   Collection item ID: {collection_item_id}")
        
        # Test duplicate addition (should fail)
        self.run_test(
            "Add Duplicate Coin (Should Fail)",
            "POST",
            "collection/add",
            400,  # Should return 400 for duplicate
            data={"coin_id": self.sample_coin_id, "condition": "BU"},
            params={"user_id": self.user_id}
        )
        
        # Remove coin from collection
        if collection_item_id:
            self.run_test(
                "Remove Coin from Collection",
                "DELETE",
                f"collection/{collection_item_id}",
                200,
                params={"user_id": self.user_id}
            )
        
        return True

    def test_stats_api(self):
        """Test statistics API"""
        print("\n=== TESTING STATS API ===")
        
        if not self.user_id:
            print("❌ No user ID available for stats tests")
            return False
        
        success, stats = self.run_test(
            "Get Collection Stats",
            "GET",
            "collection/stats",
            200,
            params={"user_id": self.user_id}
        )
        
        if success and isinstance(stats, dict):
            print(f"   Total coins: {stats.get('total_coins', 'N/A')}")
            print(f"   Owned coins: {stats.get('owned_coins', 'N/A')}")
            print(f"   Completion: {stats.get('completion_percentage', 'N/A')}%")
            print(f"   Total value: {stats.get('total_value', 'N/A')}€")
        
        return True

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Coin Collector API Tests")
        print(f"Base URL: {self.base_url}")
        
        # Run test suites
        auth_success = self.test_authentication()
        if not auth_success:
            print("\n❌ Authentication failed - stopping tests")
            return False
            
        self.test_coins_api()
        self.test_countries_and_years()
        self.test_collection_api()
        self.test_stats_api()
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = CoinCollectorAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())