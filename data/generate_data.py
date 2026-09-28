from pathlib import Path
import random
import numpy as np
import pandas as pd

SEED=42
rng=np.random.default_rng(SEED)
random.seed(SEED)
START=pd.Timestamp('2025-01-01')
END=pd.Timestamp('2026-06-30')
N_CUSTOMERS,N_PRODUCTS,N_ORDERS=10_000,120,60_000
ROOT=Path(__file__).resolve().parent

customer_ids=np.arange(1,N_CUSTOMERS+1)
signup_dates=START+pd.to_timedelta(rng.integers(0,(END-START).days-60,N_CUSTOMERS),unit='D')
segments=rng.choice(['Retail','Premium','Corporate'],N_CUSTOMERS,p=[.70,.22,.08])
channels=rng.choice(['Organic','Paid Search','Social','Referral','Email'],N_CUSTOMERS,p=[.30,.25,.16,.14,.15])
cities=rng.choice(['Delhi','Mumbai','Bengaluru','Hyderabad','Pune','Chennai','Kolkata','Gurugram'],N_CUSTOMERS)
customers=pd.DataFrame({'customer_id':customer_ids,'signup_date':signup_dates.date,'customer_segment':segments,'city':cities,'acquisition_channel':channels})

categories={'Electronics':['Audio','Mobile Accessories','Computing'],'Fashion':['Men','Women','Footwear'],'Home':['Kitchen','Furniture','Decor'],'Beauty':['Skincare','Haircare','Makeup'],'Grocery':['Staples','Snacks','Beverages'],'Sports':['Fitness','Outdoor','Equipment'],'Travel':['Luggage','Travel Accessories','Essentials'],'Books':['Fiction','Non-Fiction','Academic'],'Toys':['Educational','Games','Collectibles'],'Automotive':['Accessories','Care','Utility'],'Pet Care':['Food','Accessories','Grooming'],'Office':['Stationery','Desk','Storage']}
names=list(categories)
prod_cat=rng.choice(names,N_PRODUCTS,p=np.array([.13,.11,.10,.08,.15,.07,.06,.08,.07,.05,.04,.06]))
base={'Electronics':4500,'Fashion':1800,'Home':3200,'Beauty':1200,'Grocery':700,'Sports':2200,'Travel':3500,'Books':600,'Toys':1300,'Automotive':2100,'Pet Care':900,'Office':850}
products=pd.DataFrame({'product_id':np.arange(1,N_PRODUCTS+1),'product_name':[f'{c} Product {i:03d}' for i,c in enumerate(prod_cat,1)],'category':prod_cat,'subcategory':[rng.choice(categories[c]) for c in prod_cat],'unit_price':[round(float(np.clip(base[c]*rng.lognormal(0,.45),150,30000)),2) for c in prod_cat]})

weights=np.ones(N_CUSTOMERS)*np.where(segments=='Premium',1.5,1)*np.where(segments=='Corporate',2,1)
weights/=weights.sum()
chosen=rng.choice(customer_ids,N_ORDERS,p=weights)
signup=pd.Series(signup_dates,index=customer_ids)
dates=pd.Series(signup.loc[chosen].to_numpy()+pd.to_timedelta(rng.gamma(2,85,N_ORDERS).astype(int),unit='D')).clip(lower=START,upper=END)
churned=rng.random(N_CUSTOMERS)<.25
churn_month=rng.integers(2,7,N_CUSTOMERS)
for i,cid in enumerate(chosen):
    j=int(cid)-1
    if churned[j]:
        cutoff=signup.loc[cid]+pd.DateOffset(months=int(churn_month[j]))
        if dates.iat[i]>cutoff:
            days=max(10,int((cutoff-signup.loc[cid]).days))
            dates.iat[i]=signup.loc[cid]+pd.to_timedelta(int(rng.integers(10,days+1)),unit='D')

month_num=((dates.dt.year-START.year)*12+(dates.dt.month-START.month)).to_numpy()
growth=1+.03*month_num
weekend=np.where(dates.dt.dayofweek.to_numpy()>=5,1.12,1)
status=rng.choice(['Completed','Cancelled','Returned'],N_ORDERS,p=[.86,.10,.04])
method=rng.choice(['Card','UPI','NetBanking','Wallet'],N_ORDERS,p=[.38,.38,.12,.12])
cat_weight={'Electronics':1.3,'Fashion':1.15,'Home':1,'Beauty':1.05,'Grocery':1.4,'Sports':.9,'Travel':.8,'Books':.95,'Toys':.85,'Automotive':.7,'Pet Care':.75,'Office':.9}
pw=np.array([cat_weight[c] for c in prod_cat],float); pw/=pw.sum()
product_id=rng.choice(np.arange(1,N_PRODUCTS+1),N_ORDERS,p=pw)
price=products.set_index('product_id').loc[product_id,'unit_price'].to_numpy()
seg=segments[chosen-1]
seg_mult=np.where(seg=='Premium',1.45,np.where(seg=='Corporate',2.1,1))
qty=np.clip(rng.poisson(1.25,N_ORDERS)+1,1,6)
discount=rng.beta(1.6,10,N_ORDERS)
promo=rng.random(N_ORDERS)<.12
discount=np.where(promo,np.minimum(discount+rng.uniform(.08,.20,N_ORDERS),.45),discount)
gross=price*qty*seg_mult*weekend*growth
discount_amount=np.round(gross*discount,2)
net=np.round(gross-discount_amount,2)
orders=pd.DataFrame({'order_id':np.arange(1,N_ORDERS+1),'customer_id':chosen,'order_date':dates.dt.date,'order_status':status,'payment_method':method,'discount_amount':discount_amount})
items=pd.DataFrame({'order_item_id':np.arange(1,N_ORDERS+1),'order_id':np.arange(1,N_ORDERS+1),'product_id':product_id,'quantity':qty,'unit_price':price})
payment_status=np.where(status=='Cancelled','Failed',np.where(status=='Returned','Refunded',np.where(rng.random(N_ORDERS)<.015,'Failed','Paid')))
payment_amount=np.where(payment_status=='Failed',0,net)
payment_dates=pd.Series(dates+pd.to_timedelta(rng.integers(0,3,N_ORDERS),unit='D')).clip(upper=END)
payments=pd.DataFrame({'payment_id':np.arange(1,N_ORDERS+1),'order_id':np.arange(1,N_ORDERS+1),'payment_date':payment_dates.dt.date,'payment_amount':np.round(payment_amount,2),'payment_status':payment_status})

customers.to_csv(ROOT/'customers.csv',index=False)
products.to_csv(ROOT/'products.csv',index=False)
orders.to_csv(ROOT/'orders.csv',index=False)
items.to_csv(ROOT/'order_items.csv',index=False)
payments.to_csv(ROOT/'payments.csv',index=False)
print('Generated:',len(customers),'customers,',len(products),'products,',len(orders),'orders')
