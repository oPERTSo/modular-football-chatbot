import requests
import json

def test_api():
    try:
        response = requests.post('http://localhost:5000/chat', 
                                json={'prompt': 'ดาวซัลโวพรีเมียร์ลีก'})
        print('Status:', response.status_code)
        print('Response:', response.json())
        
        # ทดสอบกับ topscorer queries อื่นๆ
        queries = [
            'topscorer premier league',
            'ดาวซัลโวลาลีกา',
            'ดาวซัลโว บุนเดสลีกา'
        ]
        
        for query in queries:
            print(f"\n--- Testing: {query} ---")
            response = requests.post('http://localhost:5000/chat', 
                                    json={'prompt': query})
            result = response.json()
            if 'response' in result:
                print(f"Response length: {len(result['response'])}")
                print(f"Has HTML table: {'<table' in result['response']}")
                if "ขออภัย" in result['response']:
                    print("❌ Error message found")
                else:
                    print("✅ Success response")
            else:
                print("❌ No response field")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
