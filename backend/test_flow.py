import sys
import asyncio
sys.path.insert(0, r'c:\Users\xanas\Downloads\New folder (2)\\backend')
from app import flow, supabase_client

async def fake_insert(r):
    return [{'id':'fake'}]

supabase_client.insert_patient_record = fake_insert

async def run():
    fm = flow.FlowManager()
    print(await fm.process('sess2','I have severe chest pain'))
    print(await fm.process('sess2','John Doe'))
    print(await fm.process('sess2','45'))

if __name__ == '__main__':
    asyncio.run(run())
