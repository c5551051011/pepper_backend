"""
MVP API Usage Examples:

1. PHONE VERIFICATION & LOGIN:
POST /api/v1/auth/send-verification
{
  "phone_number": "010-1234-5678"
}

POST /api/v1/auth/verify-phone
{
  "phone_number": "010-1234-5678",
  "verification_code": "123456"
}

2. CREATE STORE:
POST /api/v1/stores/
{
  "name": "진스 카페",
  "category": "CAFE",
  "location": {
    "address": "서울시 강남구 테헤란로 123",
    "latitude": 37.5665,
    "longitude": 126.9780
  }
}

3. CREATE WALLET:
POST /api/v1/wallets/
{
  "store_id": "uuid-here",
  "nickname": "진스 카페 지갑"
}

4. CHARGE WALLET (Store Manager):
POST /api/v1/transactions/charge?wallet_id=uuid-here
{
  "type": "CHARGE",
  "method": "CARD",
  "amount": 50000.00,
  "description": "카드 충전"
}

5. SPEND FROM WALLET (Customer or Store):
POST /api/v1/transactions/spend?wallet_id=uuid-here
{
  "type": "SPEND",
  "method": "TRANSFER",
  "amount": 5000.00,
  "description": "아메리카노 결제"
}

6. QR CODE PAYMENT:
POST /api/v1/transactions/qr-payment
{
  "qr_code": "STORE_CAFE_001",
  "amount": 5000.00
}

7. GET USER WALLETS:
GET /api/v1/wallets/

8. GET NEARBY STORES:
GET /api/v1/stores/nearby?latitude=37.5665&longitude=126.9780&radius_km=2
"""