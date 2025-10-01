import os
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import secrets
# Load environment variables
load_dotenv()

class ProductItem(BaseModel):
    id: int
# --- NEW: Function to generate a future date for offers ---
def get_future_date(hours=0, minutes=0, days=0):
    return (datetime.now() + timedelta(hours=hours, minutes=minutes, days=days)).isoformat()

# --- GREATLY EXPANDED MOCK PRODUCT DATABASE ---
# Products now have realistic images, descriptions, and dynamic offer end dates.
PRODUCTS = [
    {
        "id": 1,
        "name": "QuantumBook Pro 16-inch",
        "price": 2499.99,
        "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=2652",
        "rating": 4.9,
        "reviews": [{"author": "Alex", "comment": "Absolute powerhouse for video editing."}],
        "category": "Electronics",
        "description": "The ultimate pro laptop with a stunning Liquid Retina XDR display and M3 Max chip.",
        "flashSale": True,
        "goldDiscount": False,
        "offerEndDate": get_future_date(hours=8, minutes=30) # Offer ends in 8.5 hours
    },
    {
        "id": 2,
        "name": "AuraSound ANC Headphones",
        "price": 349.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=2670",
        "rating": 4.7,
        "reviews": [{"author": "Maria", "comment": "The noise cancellation is just magical."}],
        "category": "Electronics",
        "description": "Immersive high-fidelity audio with industry-leading noise cancellation.",
        "flashSale": False,
        "goldDiscount": True,
        "offerEndDate": None
    },
    {
        "id": 3,
        "name": "ErgoFlow Mechanical Keyboard",
        "price": 159.50,
        "image": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?q=80&w=2670",
        "rating": 4.9,
        "reviews": [{"author": "David", "comment": "Typing on this is a dream. Worth every penny."}],
        "category": "Peripherals",
        "description": "A premium mechanical keyboard with customizable switches for the perfect feel.",
        "flashSale": False,
        "goldDiscount": True,
        "offerEndDate": None
    },
    {
        "id": 4,
        "name": "NovaStream 4K Webcam",
        "price": 199.99,
        "image": "https://th.bing.com/th/id/OIP.jMMAgmfbv9kPSSYWAeIgTwHaEK?w=312&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3",
        "rating": 4.6,
        "reviews": [{"author": "Sarah", "comment": "My stream quality has improved so much!"}],
        "category": "Peripherals",
        "description": "Ultra HD 4K webcam with AI-powered auto-framing for professional streaming.",
        "flashSale": True,
        "goldDiscount": False,
        "offerEndDate": get_future_date(days=1, hours=4) # Offer ends in 1 day and 4 hours
    },
    {
        "id": 5,
        "name": "AeroPress Coffee Maker",
        "price": 39.95,
        "image": "https://th.bing.com/th/id/OIP.OXO4X787unTxtn-mWoOgsgHaLG?w=124&h=186&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3",
        "rating": 4.9,
        "reviews": [{"author": "Chris", "comment": "Makes the best cup of coffee, period."}],
        "category": "Home & Kitchen",
        "description": "Iconic coffee press for a rich, smooth coffee without bitterness.",
        "flashSale": False,
        "goldDiscount": False,
        "offerEndDate": None
    },
    {
        "id": 6,
        "name": "HydroVessel Smart Water Bottle",
        "price": 89.00,
        "image": "https://th.bing.com/th/id/OIP.qCg-3kXF1nkcXML3KwPrrgHaEJ?w=329&h=185&c=7&r=0&o=5&dpr=1.3&pid=1.7",
        "rating": 4.5,
        "reviews": [{"author": "Jen", "comment": "The glow reminder is a great feature!"}],
        "category": "Home & Kitchen",
        "description": "A smart water bottle that glows to remind you to drink water and tracks your intake.",
        "flashSale": True,
        "goldDiscount": True,
        "offerEndDate": get_future_date(minutes=45) # Offer ends in 45 minutes
    },
    {
        "id": 7,
        "name": "TerraFlex Trail Running Shoes",
        "price": 129.99,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=2670",
        "rating": 4.7,
        "reviews": [{"author": "Mike", "comment": "Great grip and very comfortable on long runs."}],
        "category": "Apparel",
        "description": "Durable and responsive trail running shoes for any terrain.",
        "flashSale": False,
        "goldDiscount": True,
        "offerEndDate": None
    },
    {
        "id": 8,
        "name": "Zenith Ultrawide 34-inch Monitor",
        "price": 899.00,
        "image": "https://th.bing.com/th/id/OIP.53d6DTbW_cw626aa2kO7NAHaFj?w=270&h=202&c=7&r=0&o=5&dpr=1.3&pid=1.7",
        "rating": 4.8,
        "reviews": [{"author": "David", "comment": "Productivity has skyrocketed with all this screen space."}],
        "category": "Electronics",
        "description": "An immersive 144Hz ultrawide QHD monitor for gaming and productivity.",
        "flashSale": True,
        "goldDiscount": True,
        "offerEndDate": get_future_date(days=2) # Offer ends in 2 days
    },
    {
        "id": 9,
        "name": "GamerShift Pro Ergonomic Chair",
        "price": 499.99,
        "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=2535",
        "rating": 4.7,
        "reviews": [{"author": "Emily", "comment": "Super comfortable for long gaming sessions and work."}],
        "category": "Furniture",
        "description": "Ergonomic gaming chair with 4D armrests and lumbar support.",
        "flashSale": False,
        "goldDiscount": True,
        "offerEndDate": None
    },
    {
        "id": 10,
        "name": "Nomad Travel Backpack 45L",
        "price": 220.00,
        "image": "https://th.bing.com/th/id/OIP.aswnWlx_7Tdzoa-RSAijJQHaHa?w=217&h=218&c=7&r=0&o=5&dpr=1.3&pid=1.7",
        "reviews": [{"author": "Tom", "comment": "The perfect one-bag travel solution."}],
        "category": "Travel",
        "description": "A versatile and durable travel backpack designed for efficiency and comfort.",
        "flashSale": False,
        "goldDiscount": False,
        "offerEndDate": None
    },
    {
        "id": 11,
        "name": "Precision Pro Gaming Mouse",
        "price": 79.99,
        "image": "https://th.bing.com/th/id/OIP.eO7VerzIAN0k7tkY4Q9GsgHaHa?w=185&h=185&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3",
        "rating": 4.8,
        "reviews": [{"author": "Kevin", "comment": "Lightweight and incredibly accurate."}],
        "category": "Gaming",
        "description": "An ultralight, high-DPI gaming mouse for competitive play.",
        "flashSale": True,
        "goldDiscount": False,
        "offerEndDate": get_future_date(hours=2, minutes=15)
    },
    {
        "id": 12,
        "name": "EverGreen Smart Indoor Garden",
        "price": 199.50,
        "image": "data:image/webp;base64,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",
        "rating": 4.7,
        "reviews": [{"author": "Laura", "comment": "Fresh herbs year-round, I love it!"}],
        "category": "Home & Kitchen",
        "description": "An automated indoor garden that grows fresh herbs and vegetables for you.",
        "flashSale": False,
        "goldDiscount": True,
        "offerEndDate": None
    },
    {
    "id": 13,
    "name": "SolarCharge Portable Power Bank",
    "price": 59.99,
    "image": "https://th.bing.com/th/id/OIP.LS4yCjnPMF1ABU1o-F4prAHaHa?w=195&h=195&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3",
    "rating": 4.6,
    "reviews": [{"author": "Nina", "comment": "Perfect for camping and travel!"}],
    "category": "Electronics",
    "description": "Eco-friendly solar-powered power bank with fast charging and dual USB ports.",
    "flashSale": True,
    "goldDiscount": True,
    "offerEndDate": get_future_date(hours=6)
},
{
    "id": 14,
    "name": "SmartChef Digital Air Fryer",
    "price": 149.99,
    "image": "data:image/webp;base64,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",
    "reviews": [{"author": "Raj", "comment": "Healthy cooking made easy!"}],
    "category": "Home & Kitchen",
    "description": "Touchscreen air fryer with 12 presets and rapid heat circulation technology.",
    "flashSale": False,
    "goldDiscount": True,
    "offerEndDate": None
    
},
{
    "id": 15,
    "name": "FlexiDesk Adjustable Standing Desk",
    "price": 399.00,
    "image": "data:image/webp;base64,UklGRnIsAABXRUJQVlA4IGYsAABwrACdASoLAQsBPp1Amkmlo6IiLNSdCLATiWMYn3KBaFhRV692kmPL9MV4fzL/j++f6mf7TvMf7F0KnRgdWt0VVXg+cf0P+08M/zr7X5ad+/3//K8zvunnv/xPAX9r/o/QLet8tfQX93fvnnHff+aH2f6Nf+p4ln23/pewV/L/8h/7P837y/+7/9vOd+3f8f2EPLg///ui/dT//+6t+2f//Udy5i+UisSuCCJ4y5uRRzfxAU5RNsbEOX8FFVIdPLViy6lZQAjce6Ii5VTBsCihM3kPWWeDhWBQoAXIziPKvYCxOXKGj/IKl8KGDelfxn8eZBIlxp2JloxGOZ/0shwf9OjgHQhSD1deWrwAy0X3jwF6EDJO23aUpEpsiosBvEI+BuBhFivI8QA3TyfxmDb4kSfmQi9FH25YlTyj89qc5YaQFUpWOz5StF2rgik/vMvZxiqu1naMSID6WujzHzj2VbkGmGlyNpZ0bajoChiDvob6e+giac3y8/cNyQ1TLuK5ab6+1OlduhQASTycxskv4cjSRol1QZ3gliulFmqWkGTAcTctF/1pSnNGejhxU0rsgGWnFbzrDJyt0uP4KrEja1+aQTURZ6wKuMQqngfm+OuAkLIFd/n3RS1vkAY9BKOyZ0sPgsNZhjhzJ3FYdsNtPRtgZ8jk7baXh2N5EB5vcSE6b58JX+pRcv3IllSvfk+Hm0wGjU6j8UGda56/R9Zsdtn+w6peob/MEcOmJjWlDD6Gf7mxLlSfGU7LghT2TQfDzBneFnmIKhNreH97cip3TtWcc+SlGeaeq4s0h1Z1ip6U+os0Uy/XbpOpBUWnDoyxKJvGHoCrgt5lhRxr21OsKpIuJTWxq778VzahVnPVDdAKeSAJccUcjiHiBkn3EDEJmQttnMWujlVll1pYTTijJJj0xY/aOJ3XEqm7f6YkC/PpQ5LM5lXJS1dGNhSdm9vpjEItLFASpEt8m+OG/qJxQgkx5CmHUAU7TiJvqaXm3v6HWZVHmUOG7fjx3mumctG1BPxjW6xGJNzi8QzBo9TjP1F6u7lE4X3beG3FcVK1czWb1iGAQoSCH3i+VyAMF9f9RzZyIHwrvtC0yz8m35i4DGyFn3rwBhm/iGreD3VzNOIvTfeGwcuXFSfn5P2uCIwWD9KgJnFjVnmRWYLwwF0w7cb7tV0IjZi3JbF0vn9QW3e/B+Jfwh/ctbCKa/Wy7MlYPXPSZn0l9NnbGPRKT9qNmaFTxd9LI1qJ+mkSIWakpH27t2XrPH2dYxGIS11kHOg9HqDIXjay0ht7v0ApoGuyQm++O3hcSnOb0+M+hDzpL/1r2GO9zD7UmPjhIEq1T00X+8btDfa6/NMfaEc3CwCN3/1DUOcQNvemka1SoqE2mxkgdsFFGwr1Q+sy/ZIBXSru6F/Uu2Ct3nBkzSB9IClWAydo/Y04LwMauqcMcW5jbhXY0CIryaWz5GodFVomnA8lFEQ0BeQf6CuYSuQqrbouRNXuN2rtYoyXcMBefpJqbH2iDT+1U+qfL+K6MyAwJkTx+AmKjlwT6d04jlvRFV1zAxp2U8vkGL9syMmQBaY4JGzyFkCGkob+kLl4c1gLidHxfXOa7awN0ZSofZ78OHxjNiFTKXGVv/cUMOp8V8ezbzZvtY+lUrGuMyHcriqwpK0tW2dSIS34QlXTj9yNno+7IT8IRDn3HhIL9Y/j9bMt6E8mtf+++viWH4WIoxYr6hrotJSbimqzGDVMtrfWSHPhdUj3WDVbNXr26Z/DPl5DZJSS1L6kejd+HCzq7ilrTlmzDzn9BWTe7O9+t7jMFH9OY0wXBpao4PikWSZEcgAjbj+MKDlzHszOEj9yAAD+vqUP2+DxH2COywlGqeWnYbzR+snBDXFx1mZK2XFrPtLqAfIa51TWyl2e3nmkg/uaa2D+13gUJXQUtNoLzbROvAWUaT6ymNzOgPGHQCascYF23bgIlvmEX1+okDHMpujGzz/cEPdd32xiHBwwnxao/D6q28meEY+BYDRGKBF61ey9WmffXcZeOuJTAKTU1zsE+RwthM4tOXGMSWjs6ovPngejLsLUIVR6GtQmnDO5QG1h6kaxHNwYYxun5pBXmB6Y/KWQhTgobTiufLUm534/NwdOPks6Z0LgZW3eawyfqz03CdBL89p50EPtbUZ/SVVysiNJPKmPwwPan7DkLC6yWjQ5lRPuPRna0ZMuvnxTJtxHKhX16giABjttAADhPAeWZP/TUgeUfV4mdhQsltCwSWAVOpKktfGSoGkZxU/Ttg3rtXU95h1GS2Cg0ozxaxIapIFz4x4bu0IXmVrbIqYXKkdKRan84r0Wc9xegSWy0z1msh52zHcbLK0d/kpRhTRzvdTCqlLbpxYft9dUQcjJpcNYVfntlatgmtxayeTpke2fl58+g6axFWqRgCHE9q2dEDOoeeTxhM3sEJch9tVBu6pqRmfpWFqQI6gTuwV8TJPVmSzFQNQeClcwcJIQOkwPUdBjB2HKXVwmeRGw0xJ4sRRBg8omlJzg5KAd0k9g1y8M/dmdOltBeDeh1UsXrnWhjfFgciTwtcbmf/PlVWattICtDUH+eVebdEA+goJQlaw25WmlnJFn+9kVvNBvXRCPGoFS1K8Du0QuCpFuNQhUSxI6PGLQ3U/dX3r6N2AnT2d8ANZhfvupyjd+ZNlPSfymn8L8HEASWXWYi4M5AatReufCDETEiPHqppq0QHm45x4CqLFqi4lg6BY//pctMFzIJtANDA7WQzyn0NfPaummDrfcRZrTs8gNzXP7wUp3kghl7p8BLYctmyrmXA+/wlDk1wyxGaiXeVw+wF1hIKjEnQM/AOxV9nbRFCDNJarheZKTw2nykDYenfy6Br8GsYQJvMHXZPwcB1vu+qRvUBUGqCYNlrlpFwZayqgxYAMNfjFxXUD2o8t7JwNKzePXxvqdNfqQ/kptIuArgMyWEjTT1V/eLRx4HcnAOAs5fuaJxJv75LN3KA6WAM8zdYjO4X03h8ve9VhODSQ3121O9/bIMe10LbNonqwt8Wcul9bMM8Fh+PpGBifixIV03SFrq/SVb4oZermjJ9PEIhmglbkpD6Up/N6YPVhSqDZ4my5rSfPUxjAOXnvDAb3G6ZB+EWlres2xLXnq0CEdfxVWnp/9U1sdZWOuJVE0j8Ondrd5HmuGv5YtUnvSvJfapv+DOWMX1H4qmU1IEkciQlkE1M601H9iiBOpes/ZY9PCafMWLxpH8GKjumr7Jhk4kwDPomvfl0vFI+Crbt6G1w6hDmj3kx4IEYwTXugmVfn2zOs2kDjOO/Rn0NsRtoGDRal79jCBytMBWqYed9Dw9gQoax0q96wTopP29ht0+cnHQfdMxQsck2iHHkYNb6ZEXbVNgkrZ03GpvSukTVLfJTF3Zhr8zraTKsEqpr+tVM/ZkL/x6ow2ljhszpH8CDfzo7XlHNds8uUfwHDBDLnWpaAmKg/cki+CnHkH9hdMvooHWnBcWMmXtJJfqcq6zmAFFOtCvV6R/+k47duLqVx8tBmcOH8vW2Kr7XkoxWO6RCkkpxS8w5wmb7JxzNh/282OG3LskLg6w7ruWKxZvEtHFHMYVg1XOUg2Esf9UMOj+IDS4vwj7TZjGaf+b6MvWQnQjSZUDT5n0+iYqRaJ4WiJzJukV32U2O9lE+4Dgl8conIwWOvhyzfn0jy8XbbNGLli0dp3oXpEjhZqJ3/R+JwsEFVqU59bVHC0v1gTctYQ/Opu65mV9f59z9zMqh354KgFraLMfYU8mnB+lf3uRf4TUYlJHwlJGLroWY/6GALINITkwORWqxUnIWqr46VcJs9rhahiuSnfesZ4/K/3w7SOqloncShTJMFdzjg06RpqTC+V9biXL4xWrhUbg5qbIiJg6+7YM1MA8D99uCtRNVIT+RmuN7dkhe4Wqr2uvT4Wm4wd5cF/P5MVuVzbTJKFOOGzOUxwSXSOH3H+GTnhjkY1yPV6DuBpiqnsHkcbFb1p+NafgSf7sl2Lg6ylV3JShTF3B8h1cwTL5UWXKkYOmhxQeyl8FD378hFoMucoMrpbm8Cc0R9Yp93brjWc2DaFEmqnST2nb/JlrtiKBcQk+OO/b5krw3CncT+IVpIHPHFqZ7nRvcDq3uqUSeOHDrdhkYaDfI6c3zGJ5TfaZ6OPEZQlOreQa+IEdkuRFjPWmp+taVGW0UMbss0h8838fi3x+3PoNVRHotegHO/8RokQKsSftxb8xRIAtgbeCHGwRFlr8YvC/uaMqg3AAHiSNM7C1YNdtEG2gqbGFB4GE6XTR22zacR76fdaVg4JwZBJ1sDpjUjDwHMfqO4Z8Rj94Zx/AtyBDsBGWxL4C3/trrANwLX8Ydlkc329Vr7/SsWnVG/VfXsdOOmcQoq35TWGfNXtO+kkiuMC9JQ61Pd0olkp/QYWweSH/WdT9yd3FHjziam9ThzTwl+gmaHLM5VExlwYxiKOf6O4VOrrIld9s6t1/2yMlJBp6i7fFttW3Frd+WAGANtcbqqFxe91CRYWKeJ0REycLZ/95SX0NSZFs7V8bNfDYY3ynzMmgJIVM1GyZrQzZafwXp2qTn/21a5kqH0UJ1ldf5aD+REo3rpltW+XT8dP9EPNWjl9dV/TcJOzYh05WCTZVxVTmqtAQ30D++9gzptz9eUfh0/2E80ygzu8fJUchMATE7gK1P0SwDI/PygCe9fU0XWpYSVLbYXWTd38ZWq/ITovQM7wjapmSr4AvdcrozYGm5+jVkruN+v0pEaZtcZDQOcW1gGFm0wfPKZdya5EK3GxlW2M6pkyqlPHq+PflyWOaXuUtlVv1k4gnkWZJsnpm6fBBMA1BhwzOuG9C36U/+Vm4hJQJhvDW1PV/JoEPRZbjnLynPWeirI9i/ushqK6LC9Mjc/1QE7pncQ3F0AB5PDUuXfun6pw9RbLFq+Dk7WnB9tz0YztNmdImD1h0c1GETfeKdtBsOSko2awwv35LyVzigqusGLskxNAUcBE6yZAlxTM14gcqFSo/f1mqTSElOrCND7ez4TYD4ypyTPTOjVtT51mPc2Z0NRdKrTgxQ3ePt4q8F2Kfp7xDcbO812wS6zoUBzc7sOZfbgrh18dpTE+Hn+A7x2ApY+geMEBxx8iFGWhAh+eOFlOXhc0aEq0j6cFRo6ofm9hqkUJcPe+KfT4rDd5b2v8LlDwpq86uar9AFe5xiozzHC6OoW73NdfxTw3L4+6oosGppaRX0e11tvlQr9YTWG3H9WERtLYRXUMm1/wzx9Uw4pesb/G/k4BsYdjZRnX2rg8n8RDzs5K6N9mVUr6WrO6wwFeIFHr3jGu3UjRoBTE+S2bwwgfFJCEysUCPCCvYvcW7G9PSZAvBJcJhiuKf90DPRuLVjnxkepG51HmfmH2lIrAuLIVhfJNnv4vVemZHvGmfzMpWs4UorVqyc6pXH5G++RhnNcWnMeyddgOBZTgHkHpbPio2SBpLjFk43kmln71SMIZMhzck9ZybeQXEbdO3qAcRuRzrgfwZ+355FbwVr1MKoQNgPiYZKc+EbnzgBn6R1HHTFHjASUeuxnjp66WKpb+4j/ppW55qK2nOAVrTolYNuJ1eargNAquqjZ8ich+9j5pdkaIsAcuYEuLMxkPmKjc+2iSMSb+9o87uAfPibPQ1B7kIhh7uGFYZl6e6gS24R9fyNjkbxn5QAcZjYuQt9C0cW0StIgin0mwfjP/OKEVhLRePgAMeROOMMWp5duzQDeeBRZbJ1xd9gOGQ7gEFs7TEKz9T0mHRAuCnP/Dzq6I7W1WBU6GvpBELadSQWqaGCYIT9BvVMJbh8UgKtfLO4d7JpWwYqkr3qN1KfyqOoGpKN4RfRrJBwe3GfjmVrH0abtpCvrr0mJZomKoEzs65xFK927oBwnItcX8G2fWAVv9WOFHgiZR7xkY07DrhEYwMu7LiUMnrjl8x+AmLhJEEc4Jz+J4Qe3Yai9Z2VZYn4FOv6/fh5vnP/ZQr72jFGvu2+pj3hEGay/NpiaMwXigGOlWuWxSjx6DsXUuoFujd51cOsw2FLeSb+vXjbVGGiqORx5R2tISZj2RvRcv1FKWINfR5m26HQiLuc7gAGptmCkF/KfqdvS3O4+Nv1qRoz+fU+Bu9niiSkl3FgZnAzDX866z0Ts82P0p/zQlKFizd0trcpSBzRbHdbHlS8gjK9LCAzN7cBmrI3s8InHoxtvv5lMX27U3rSkHc39hloAUq8hou8WnOaAwGTJ9i2gLwfyoRHebnD9oh8uMIdZep5WOzCYtNa+uRjYV1innkyxFX5sQi7ehCRAkRIIuxqckEJigUjY8shZjnpWM/e03vvJjfr5bO+lmzrhWCsEpCpaTOm8yYRJRPiIwW8EMqFgZ6qoTLNOSL2OtS8QUEaGHPYhY9RZu+qCYvgSvBnocdeeCTsk4csszJjF67So09XgOFVRQogkzlSYP3+tvhYvjBW2oYvyDnbswE/yjrJsfuyfNIOG9eFo0Ve7xsD3/yprPUHYLXEZmdHWnutF+cR36n7UPzF7IpuLeDA39kLplPz5NlDwTg+FzqQ2ovTUS5Ej3RFYoRMKu1pTxBafqRfoyALmsyVcWfEQo9Z1/0uCX25/FPfc+agewfXpwn8dpxMNnQzIQr54lx0MPdRzxg/FmN+SOedaFJHTgBnr/H/TNk6/WHRakzqIMtRPo2oGndLgA1D4NwQl9uj4ASghH/SLhvwZLn1AbNziGMHbIHIRBLXvq2HAWH6zAHjazyEcDWMv1D6arzB2c8g+6mlb46674+IRevsK7WJcjx/iK6SYkCPpR1y3VmkJsS1fpU1tSNZWM2AirOQj/t3xPYLBAjmPMdpBFM8Uv9Mujw+3uwC3jdz3krKm6Fq/PSXbQgtWNwEmJt6LhOdDwR12UgfjjSJ3WuZDzGCjxWxXTAx+1XSCDBFpgjDlWHFwZu/kutT2HoETosGRqGLB5xKjUwP9F12CdExwociWOUBRjEaT9UEnBzuP4F3QXxUPurW3YSlgVTxhHicKC9JW2ZaZJ1r4yxINHYCgMPzG1EKrbdnZpeAMtOcPIciReA+T6JsJswXso5+3WB1/D1Ub+M1Lq4j17HE+Uy8I01r5dxjG82VUtLEqN30y1l/Y5I+fObZLe4IgH8XS0ogoUbg/mhI2PXdf0MYV3Xq2IM+tN6nkw5HItjTi/M+V1Wx4szl8sFv9ciccaJkXr8arKOTGtuqDsaXWKZYEYzeUHM2G2VQufrKJCJfEYaFRTi/+xXnmkY7wQV/MrfnQVBJ87dYuNQ4y2et9Edh+GojD2NPVhtB3c9J/E5Lxqb9gooHGdyCC8EJF38SZ33hDbJWrgbenx63g5eO327I0QAr6md1ZUtKupXih9UkkCmg/4nzcnH/kTUCtlNqO7LaQv+vMruYCFOjJbZSOLcRvq3758GJ8HMLfgVTTz1GiLk5XBoxbPUXcm52FTbNEPrKQZLnzUJpCyNvGDQE0eUOQSkFDc7NcXJCVTGnquPyLVoWm3iPz21sQCSmHgure/tZmDn0CCvVcE79e3+WOAtHEVN/sy2c7mAeWiKiVptig8hw6XswJJp6hBm6AfPByu4uavp7QRwLVwXR/BG6KN0+YX6o93yMWolHWGK74I0u7IgHMqv3jJHThxyQom9q9qg6PjPfnuGMnDuG01/ZSDIyVePWIPlE87b8jNv4P8zN7b6EydIFFn32vBoffoOEuf+8YfjklPIaUqcEX4FNvQn9MEVs/HqeQRWSXIBWLsWWSwmtUItINacJNcjScK8ToNTLRWx+qksSDntE5NiqHiEuha9q4JJM4ySxlOLPpZm83Z5OdjWOAxiDBzK8weALiuknOSv4MlFcu5h3fuQzUbCOXruAu7eD1riGYFFmrdSdft+KXmH1+WuCna8vDB0vEhfEfn+j6eXhW3VWgyW/n4NNoq2IkxOx+2BkWWQNsvfH9zHLL1p85EJhrtDGW1nmGZEeZ6lEgDzIDTQL3T1cdOc5aBaRd/HCW86pNzQKUPclhP2F/wcjitVopBTVyJamDsQGMyWGqGWSDaImwvkWbCOg7FtcpJDRp5x5gmsjovOC6Mm7PVlkZXBd4Dvnq9KvqPQdFH1FfnSCYQdhUzB+Gbkm5BEWEYbet9hozyDnOQwXr+NnO7cZ2smjjthM0EPeBk3zqrIu+XdYVfLPbfIJL6zcONZKxBqmw/zmy2XcfQ0to8focAQKboEIvOXmtvnVj2AOxlZ4lCHc+8myTJpSmoJm0rM0nL/jo33xSzlRoYVDCiFMx/6Nq3O3cuERH10fP8Z4PXQrjw0nvUxk6+f/PZgH0qqbtHK9V/wVkvxeIXDbJEkAiPbdAqFdF0oYqp5xUoKfC+HG0Axsv7EXmB4aJ7CCJMhj3Bipa5GYTQhKh4cNpq/r+7VWTLDVFf9RSHqvVn6Sn2GbHhnB20Fh0/1K7iVPPv5CtfQofkwMD4KfJWd9Wqc8u8YckqaIK9n6xJbw9SodeMo0o0KRPDalmn1gPu3C0l+9KrnXarqLjXB+fFDjMj9Qeh3YXi/ODsalxMSBM3KmkgqSU3TcnVvvUqJcofWtFs0pN7STFFo8AzB89VRmLAmSg+KIkz9cR9R2EwzP0DEEoSTM0//SpNu3wORkkYCfYCtcsL5b0CYbIzVMfOuRmSj7x1wY5hFvSbA6y95X5luZZUk7VxojPmxzaPWo7EgeI4f7JwmVzhf70AbF1e3xUMurv681WhPTBUdk4KEu8QKVDBlvoOGriWiXI3KtjEIeWNqL+FDbXfbf6TBrdIoU/LRWF3QLNQGJGVftHFQ6eakMlEXcqcV0qDuErA+zrEDQePGgC4kz6w2cIH7FtcCyvDNjmij21VX6FfuHMF3iauAjENLbUIby+C4taCUE/DVZG8Rg1/S9VS5rDzA9Aff97FR2ehCZUw522ZMtI9V2eYZu5ZXzTjp8Yt6HUTFY7nGdjvENyS1XxdRxDk1b1bLmdmf1XDLhDP1M09qBkbUhfKoOYj3t0ypXIsX5XQefApHN6eNrIOL2ainBSP1qrDhvC2TP8aOof2XTtuIVZtlT708IqZFSHw6oNAq1KqIL8/xOmaJ0wrjqdJ89oeXLmhuS/VLtPRIQQyhu1kHHdKZOJe/KI4NcHERL67JPhmkoli0BgPAT8n1D/ubSZF6zrqarwjiH+/uIli3IPLrSF+RweN14s7QgkkcEe7L5+HgTmj8gc/uLmWI+ZHENJt4VhNQqquAWtzIMHWTd7TB/dYdTH1MUtRT8l5iAlzqB0Ale1cgCPUq73KOPevCd6bn69ogOw3jF3RCcOSU84QMICqgpYBaE3trJuSO9GbzXrnLdWzF7Yo3tPYTsPTbbeuHQPwUZbwi0X8FhxJ+xnCddkBUO306j0wFBQe+w+OEUH4tVlU/kzIkWfdhRN1lEffJF8EH24xcJisDLIpnkH8GKFhFqnwBWD4T11QA9OyC3HSEdFIX4G4n97vOg6nM6ETylJQLpl5roIxxQ2PTNUIJ/0vlfL1cqURmYHeA5xRNyEb5NPgfNJ9p1gxYxAyswhNBWGqt6HKXzywWtnIRjD8cfrsFVFON4off4lQgc7bkSgnczh3T1CY58E3gQO5op4Y5W1Z771VHUC50BkVkgTPkAj6tSvVyeScJYywyX3RAejggzHliooiF/G13wK+mm12i3MLKX+Q3OfLamivvzao3+XOVbtWb25LuVUa8ZoTbC/lv1bwGzJ+vHdJoX/1sHCuJYC6IGKeqQDd2Nh5q7plX5BEgK+4JrHIW2Xt2efAELcXM4ex3qK44Mioip/oGh6/RhzQvFn2i3/d+IN07FXTkD20fejzRGeaCa2ORt2qhONKSZ12WJIk2duJABCEp//DA7p1ypM8dVbiB4PumV6XDNYyh9mbzbNZAEdw78LlCwEQFfAFCasvcTSgck8bO+Siypzmgd3DNs7rNimurLEEG+ZAHCqoqd4E+rbTwE1FDOKqpmjHs/2SKlCSPGE6apttZKKq8Bp5khjR06Wc/jmdpcpE7gpbvo4q4aKQcGlJ/O2REOWrFjiXr1l8RP7Ha2R5QRXiAN52UnKaXIp5csesB6iVktq1j39+jVrOHkzs199MrZ8+XxW15s2o/1UBqZpHxHy88QzbFWm0Avy4dtUrUCc/JYszevxxdgMoBU8imtE76VyDfffDuib4xb2MBb8QefrTrwUHxtQJrNDAFeF4YBOAmUw0JC9Xh0w4RQfjg5CVWu5RFOY3p/vuzUfgmbPxmSZKTEGjwOVWJJPCGmB9SabjsSNmEdGH7XLznV3XwYu2WLUy1zFmLhmUPXVcyTnJ83+BM2n/UEm9OZyNcJZz5GswOJ0HH2gNCqh+WGB4OqQiEv58uXjV4kuW5WsHlQiUHRYjFRiQLrsgop0TXOz2QGqgP3Gqv8eyIBrVoOGxiwJHCggS8DOiou7nIWCsBDwqETNmK9QuzgaXroBjeEyLtynVzwvpReCtj9g3ehps9TfgTL0SQQ8Btji4cP5CvRcuXQpoTSF92D8BlHegSbg/uH1BrS1pNbA22Z+FIbo2UHejKVMMA6zK8xo4s72ai/0puAZj9kbmdPAJugQuJXQq16w+e53bLlX6COEqNmXBURB3fjhGHuc2QPjHXU9d+MLZ8W2GcSeX20njEFVBil9phJCCmoCQoNcdySPhHfkD0ALKWguZdikMb4tfVDk5WPXaDoLXWQA8DDqSZ86H6OM6x8om4fe2SrsBfow4+O+ihbE+WvBchOSC8Ekzj0qbkt3rsz/5k8wukW1yuPNW0gtEBLxJm+aV40MbzE81w9zA4XvxvesYbW1rKT6ZG+fTJexcD1TN0lcUoSVKcjNWdjT6wduuJX5ooU3u44cmvlBbCyrv3A7CETuq3g+1vfDibuKZBVsSyH6536mkbONBGFxAkJEo28ZS3n1o92/Qj6UvZ6iSU1kuCCQxW3lIrPyvWgnZS19Y6RlLY9rufm2BuZLEx+i1G400jNDEK6lTVFH3aEsJe4iYLwFqQ4bhv22lxJxB/u8OgwCFX6RNvyvAg3rBUtAPAv4lYrkr4hfWv43sPZ1TfvDBDFl/07qf0z7RAHiyIJDm42/fqol7sRZlEc2n1cmJSLcjVseqbAQLGeIW3FIhgoOmCQj9aD+v1+71eXaNtF+GTqR7no1Z81eSRbBS0tW6ubImJWKW1xO+9xnQS6Gm2N09hPMHD9aTbH1CY6w0NhyRTTS5+3P6StOGKSmhNek8QKBWc7eNHyU11B5GXSdbek5Qbz10YMXoL7Xp/9zcLFAq5O7b5o9xY0T/2EjgqxMfhxxOrTrdABGpXI7uC6XEXR42deTnnOaFt+Y1OrOlZUkBjT0YNwibsO2sv17YhocH55xTAgn2eF1kUlVzDy1OJLWT4bsTWOJKsnDjsZ7izGQb+huJ148Ceq4V3Q81AWWZHYVHAD5aiNun+GPZ0KV9Ns28LoOtvdL1f0VQDlkySMJdEcYz79dI2FsWnTJKS0XqCAxKpSAY53+HwOJVeEwd2Myc+D9sHfLdSg3x3d6APtHu1h2pvkTskeHUvZz784XQYtQDgfDq4fHLob48NfyaEewS63BM/z7kFwLBbh6Yts+RiCTUo61MtJa33zOOy02NnPY9yCZfyFtI5+eAHm0aofmSA5Vr2PpdGcaEm/odVBoZtKaaLb5wHkDzN5LnYGGtrijkQ72Ramj3Zc6zNLAwonFV1mCSOVZ4QEm1xqujW8ULsV1apWVkKqTnKRzw60t6s20uUo7jg5Pzelzemhe+K+fQM7GJ2ezGYhIX+dpIP+4aEZYcse6AE3gM2g0N8vp9XE+hw6SYsMuVitzlULe4FjUPUULl99Sivd9u1UGmaw9AtqOyqagCbzyjKv6S69PU/7h2IJl2IoQPrxHRCtqokDY8Y/E2oDXAeakKy6j4/K9cQTAD+4Fwd4mKR09V/KUEk74ZwRODWKXPpd46P0D87HJpU1VOoGp2Bnz7B+JeuPCQzrpLli4/z9TBfuQrB7ltm2qdIXy/sYpHWc5hDauThF24ZqLOYfTOcuyVxUiTcjNEHuL+NBmVxSGmiFB1Cr+SdDexRwzdvbt4Fvaf2Arr51TSRG3zlAcBEX9N2bJmmOPjENYpMncV5EiAenotKbwvq+tm+ztgoxr3OC9grg9RXTXRB8p+dkCewkD+sNR978rCrEs1Cl41Or5Zq19QKO2kK3X8IV2CYRBHubnqdSW8w4tO42f6ZfHPOUZpRMtsSPsE25mMcwjp0jvK4vefLrxpKLJx6KnjuNBEhwYVBN3S1Dgxfjpdj/h2qwOfHN5196Ym+uWWWsTwzTDgHwYt1XJeMPQbgxxFsOBRQpy3VxPKKR13ytCUF6ID3wko2GzS5bJ1mgzl28EdfX1b8nKCrziKViJgY6NZDokUyE7aQMDwbjhy9mi1DcOJFD10GL1mFzMc63c8QHpg2pCfqcBEAWAz98ihjI0Q3Ud1UYhKv/FSm8T6DRmeCvJOgbUEulmIeMmkpZRGvlD40ghpjjiA7VdGQGOuQwlaev/R+NpA976r9VUFsFl6Z1s8lXLPgHE/CloghDvi3VTOqSliKGuo8NWipXGcrXlhitEUCnIMTlSxRRkrOzhBSndZOmwY1OPlOkrVZnHKAms0kwd5hp0W44nqXchSS9I5wu4+2kLnUGyawhs4nWu15KGvAW3UqTIyGVLM8iAWC0m3OO64wdtE0vmebcevRBayH8VxZJUEB1rwsKQxlF+86IUGZYDlp/LV3r3xcjDBxJGpJ03GaPbwIpeU+FZxmfoxR8hz51vr8flChj4KoTV2xC5+B46Mo9h4NW0E1v9KNpy45zMjpTXQlk0OAvxUitwCjkmW+U59rJDVoMV4mLWpVjJJqW7TbP9puo7vpwwvre8NaF1UGf/gXH8cQqQ65VDyKd1ezA7inPWpD41G9sVDjziRNzk5tmbrJ/HnfPnmMi5UYxnfKurSHJOBbHNxzHlU1fURv4ClSADL3sUZ84ekAN7yrMjMwAYO5SrKT1CLRPYg8GvedcGvKpCvo1hwb8XotQ9XQn+uun0tP9xIfXI1mBj+esG0Ai7ABf4YO/XVyfWvezTTMkvuK9pNhteKDKHU2fCqcsxKMtmNpXJSG8ZcsWW10A8XnbjRU7Xl1A1NxPec9nPdsu9MTJFgdnhVpu09FDled9LjOB4s1cYuqyGvFOuhpmOjBL0g8t+i2m2Bc5nDeqjp9WPlzEfpdCMfAQ1LwY/eKBfyTnv3IngbJ2CBFYt9iYObXlSuIahF7uvRig9GsKyb8QgWhyS9uOmKHU05Tr1ntQzmui4uTzp4j99FUFe45v5HjBcliTZQoMPPqS10bJREs4Qli4BizKTfEPP18ySgS9GDtQA6sJGKVBMMonqtn5xh+3f7GS4iVRAivupL0BFqUZEoMynd3yjLmjpvI3H8mlOI9xT6sKayJko2QtS8rO5TymGaNtDWFCJgZBLf3ocl3oKH3tgb3AzohNTICOGVKJemiffqHRAIaPKi3LI/qRHnYJLb94H9GDna31294Fu2CIQ09szc+grsLDoa3LgJZm1Fudqkpqn8+YY41ZxsHEGnUjOVL59K4JRCK9E68D4Pzp2oak5ZE4ksf+oaaH30b0rDgh8oNR9CBcmlLXpde0LgSVW3QYLHkMp2ogYhGkZitG7gVB4Hm0Im8qeXXSwh6I9PVCMSxKHS0qatB73AeJQIXOID+/xOTXCDrLQ5BcgRidJ+YTWWQ2CXzp8C6z14Tk5C4lhpcxjyq4bTqliBD+Wngb6fyVAg60EBavLCbv8SgnsutzaQYXJrtbZhdZltp7VttLq1DIAvofgDR5ECKhXmziBNc7ORhPqAVdt5qXY6HwGigUR2NbV/J2FBzHEbChvjm3gB6DoDCFUf1s9nM17zFBpRsOoBgIBly09l3qONQRQLVk1e1u+PGwKOixpfXb3/nkEVG9kDG7v2Qjvz/KJuWVoTKAnxkkuQgfqGxoqzdsfay+5IzeYXnrtEMvJLh4otleWefmcnyzbXa1HYbrWPwCsAwZObTMnAsu4O7q7I1yxRpLtqyA2+1Gt80cQk/lViZSah/XQObZZjvZC3gZR5o8PXpwOrJU+JBJRHjI3ZQmyuP+Gmsf0JK+HolFjdxom7XvrzzBDDQLwm269F5VyDIw3CeAGS20YfHRl363wEmj6/HMkimVLcFIENWdjQA7L3r+HaqFufxoNez+3j5Mr+yMy9ljwPDL08pKyptn4ho2kFCiJvDAvAR7E2sAPVgm4txyXdDZ+EVQU6CD/cLdstQqTG1qBpXWcSJtnA9oKc8yezpnwIDmpQ7VhkZYbOOCnQVnEjXFTf5oQJIxoV/ESNzfWlYJvHD1TV2w62rShKUrx9Nsk5CM3b5GgQs9WoXexKA4QTJr9gzocNR6e5Cv6vuLGUdaee9O7z1JVKetrR4PUfxcERkHETatUqEOfjg2ET2mDMXHmqxG91wba1urmq458iYiUV3CNAuToLEXoL/M0F2Tt/zW1jJZjJbg/qf5Tfh7dbDicE+L+T3tWLK0u5JgU8EI7hIV+hJF/5ifYbGLrihApn/rkuomtB/t1SPZ+ae90Bp+D8Zt/EAEdctiw0Zo2R54LFpKiOeH7j2OL1cbQzK4aVdoAgmrAlkvwUJTay95TF1G2/TodP9XMkC04a/9LMK7pktZ0xENi7IALZeKkXIZNM0BeM2vZBYVe21ogb7VlvUYoPwpaZgH3nbBgPXLsYt3VzkC6YMmYJf58jHKL1oEIoVOxr/F0TGYsuiqRFZlYiUo4cnsMIDu5hkSakwBRVBdt9VcgMJRG7FHavASxw1nQKG7oI1pjLcXfwri+rfT8ecaKRaDWIscAgcsotK7FVKGfMvpu/k0erllCbtx60i5t2drN2S4TYDMlAMQE7qRc/nf8Tgxy67UGK5DfROFkWW2JtJpH6vmwa6MbLjOLxhk58Sq4E+HVfsps5DeG4bcbV+8oLo0SJxDOYXZD8Jm/3BMSbU809BST6aWhD8GLpC8JXJnS2DIEetWYMvG874+jK0LYj+NXPlf5HxJ0fBtM01tBc2+lHGxYXaNDJXQym4Dv4lkO/vdPThWOjcQ92j4YtVlz5XH8EQUJK9h6ytaw9H0Mo5vS26L4bAySINxsJSmGB7Ra5PND+MVWfYAAAAA==",
    "rating": 4.7,
    "reviews": [{"author": "Liam", "comment": "Game changer for my home office."}],
    "category": "Furniture",
    "description": "Electric height-adjustable desk with memory presets and cable management.",
    "flashSale": True,
    "goldDiscount": False,
    "offerEndDate": get_future_date(days=1)
},
{
    "id": 16,
    "name": "TrailBlazer Hiking Backpack 60L",
    "price": 189.99,
    "image": "https://images.unsplash.com/photo-1508780709619-79562169bc64?q=80&w=2670",
    "rating": 4.8,
    "reviews": [{"author": "Priya", "comment": "Spacious and super durable!"}],
    "category": "Travel",
    "description": "Weatherproof hiking backpack with hydration sleeve and ergonomic support.",
    "flashSale": False,
    "goldDiscount": True,
    "offerEndDate": None
},
{
    "id": 17,
    "name": "PixelGlow RGB Desk Lamp",
    "price": 69.99,
    "image": "data:image/webp;base64,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",
    "rating": 4.6,
    "reviews": [{"author": "Zara", "comment": "Adds a cool vibe to my setup!"}],
    "category": "Home & Kitchen",
    "description": "Smart RGB lamp with app control, voice assistant support, and ambient modes.",
    "flashSale": True,
    "goldDiscount": True,
    "offerEndDate": get_future_date(hours=3, minutes=45)
},
{
    "id": 18,
    "name": "VibeTune Wireless Earbuds",
    "price": 129.00,
    "image": "https://images.unsplash.com/photo-1585386959984-a415522b831d?q=80&w=2670",
    "rating": 4.7,
    "reviews": [{"author": "Arjun", "comment": "Great sound and battery life!"}],
    "category": "Electronics",
    "description": "Compact earbuds with noise isolation, touch controls, and 30-hour battery.",
    "flashSale": False,
    "goldDiscount": True,
    "offerEndDate": None
},
{
    "id": 19,
    "name": "EcoBrew Reusable Coffee Pod Kit",
    "price": 24.99,
    "image": "data:image/webp;base64,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",
    "reviews": [{"author": "Meera", "comment": "Saves money and the planet!"}],
    "category": "Home & Kitchen",
    "description": "Reusable stainless steel pods compatible with major coffee machines.",
    "flashSale": True,
    "goldDiscount": False,
    "offerEndDate": get_future_date(hours=1, minutes=15)
},
{
    "id": 20,
    "name": "SkyLens Drone Pro",
    "price": 799.99,
    "image": "https://th.bing.com/th/id/OIP.aGygeH8jqzx1DzSeUf3aswHaEl?w=264&h=180&c=7&r=0&o=5&dpr=1.3&pid=1.7",
    "reviews": [{"author": "Daniel", "comment": "Stunning aerial footage and easy controls."}],
    "category": "Electronics",
    "description": "4K camera drone with GPS tracking, obstacle avoidance, and 40-min flight time.",
    "flashSale": True,
    "goldDiscount": True,
    "offerEndDate": get_future_date(days=2, hours=5)
}

]
OFFERS = [
    {"icon": "💰", "type": "Bank Offer", "details": "10% off on HDFC Bank Credit Card EMI, up to $150.", "discount_percent": 10},
    {"icon": "💳", "type": "Credit Card Offer", "details": "5% unlimited cashback with QuantumCart Axis Bank Credit Card.", "discount_percent": 5},
    {"icon": "✨", "type": "Festive Offer", "details": f"Get a surprise gift on purchases for the {datetime.now().strftime('%B')} festival season.", "discount_percent": 0},
    {"icon": " EMI", "type": "No Cost EMI", "details": "No Cost EMI available on select cards for orders over $100.", "discount_percent": 0},
    {"icon": "🔄", "type": "Partner Offer", "details": "Get 3 months of AuraSound Premium subscription for free with this item.", "discount_percent": 0},
    {"icon": "💸", "type": "Cashback", "details": "Receive $10 cashback as a QuantumCart voucher on your next purchase.", "discount_percent": 0}
] 

# --- NEW: Logic to randomly assign offers to each product ---
for product in PRODUCTS:
    # Each product will get 2 or 3 random offers from the master list
    num_offers = random.randint(2, 3)
    # Use random.sample to pick unique offers
    product["availableOffers"] = random.sample(OFFERS, k=num_offers)

# --- FastAPI App Initialization ---
app = FastAPI()
generated_secret_key = secrets.token_hex(32)
# --- Middleware Configuration ---
# Session middleware for user authentication
# --- Session Middleware for authentication ---
app.add_middleware(
    SessionMiddleware,
    secret_key=generated_secret_key,
    session_cookie="session",
    same_site="none",   # allows cross-site cookies (GitHub Pages -> Render backend)
    https_only=True     # required when SameSite=None
)
# CORS middleware to allow the frontend to communicate with the backend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://10.176.55.253:3000",
    "https://karthik5529.github.io",           
    "https://karthik5529.github.io/QuantumCart"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- OAuth Configuration ---
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- API Endpoints ---

# Endpoint to provide product data with search and sort
@app.get("/api/products")
async def get_products(q: str = None, sort_by: str = None):
    results = PRODUCTS
    
    # Search functionality
    if q:
        results = [p for p in results if q.lower() in p['name'].lower()]

    # Sort functionality
    if sort_by:
        if sort_by == 'price_asc':
            results = sorted(results, key=lambda p: p['price'])
        elif sort_by == 'price_desc':
            results = sorted(results, key=lambda p: p['price'], reverse=True)
        elif sort_by == 'rating_desc':
            results = sorted(results, key=lambda p: p['rating'], reverse=True)

    return results

# Endpoint to get the current logged-in user's data
@app.get('/api/me')
async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# --- Authentication Routes ---

@app.get('/login')
async def login(request: Request):
    redirect_uri = "https://backendqcart.onrender.com/auth/callback"  
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth/callback', name='auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    user_info = token.get('userinfo')
    if user_info:
        # Standardize the user object before saving it to the session
        standardized_user = {
            "id": user_info.get("sub"),
            "displayName": user_info.get("name"),
            "email": user_info.get("email"),
            "image": user_info.get("picture"),
            "membership": "Normal" # Default membership
        }
        print("Standardized User Object:", standardized_user) # For debugging
        request.session['user'] = standardized_user
    
    # Redirect back to the frontend's main page
    return RedirectResponse(url='https://karthik5529.github.io/QuantumCart/')

@app.get('/api/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    # FIX: Instead of redirecting, return a success message.
    return JSONResponse(content={"message": "Logout successful"})

@app.get("/api/cart")
async def get_cart(request: Request):
    """Retrieves the user's cart from the session."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Ensure cart exists in session, default to empty list if not
    return user.get("cart", [])

@app.post("/api/cart/add")
async def add_to_cart(item: ProductItem, request: Request):
    """Adds a product to the user's cart in the session."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    product_to_add = next((p for p in PRODUCTS if p['id'] == item.id), None)
    if not product_to_add:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = user.get("cart", [])
    
    # Check if item is already in cart
    for cart_item in cart:
        if cart_item['id'] == product_to_add['id']:
            cart_item['quantity'] += 1
            break
    else: # If loop finishes without finding item, add it
        cart.append({
            "id": product_to_add['id'],
            "name": product_to_add['name'],
            "price": product_to_add['price'],
            "image": product_to_add['image'],
            "quantity": 1
        })
    
    # Update the session
    user["cart"] = cart
    request.session['user'] = user

    return cart

@app.post("/api/cart/remove")
async def remove_from_cart(item: ProductItem, request: Request):
    """Removes a single item from the user's cart in the session."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    cart = user.get("cart", [])
    
    # Create a new cart list excluding the item to be removed
    new_cart = [cart_item for cart_item in cart if cart_item['id'] != item.id]

    # Update the session
    user["cart"] = new_cart
    request.session['user'] = user

    return new_cart

@app.post("/api/cart/clear")
async def clear_cart(request: Request):
    """Removes all items from the user's cart."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Clear the cart
    user["cart"] = []
    request.session['user'] = user

    return user["cart"]