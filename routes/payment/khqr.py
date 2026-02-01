# from bakong_khqr import KHQR
#
# khqr = KHQR("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiMmU1YmE4NDY2OGVmNDJiNSJ9LCJpYXQiOjE3NjQwNDIxMDIsImV4cCI6MTc3MTgxODEwMn0.KdeiZJ9d2_vpAkIYAdGTOPuhj_OD05km5lMrHA4qR94")
#
# khqr_code = khqr.create_qr(
#     bank_account="lim_chhayhout@aclb",
#     merchant_name="Lim Chhayhout",
#     merchant_city="Phnom Penh",
#     amount=0.01,
#     currency="USD",
#     store_label="Lim Shop",
#     phone_number="0972443249",
#     bill_number="ord001",
#     terminal_label="Lim Shop"
# )
#
# print(khqr_code)
#
# md5_item = khqr.generate_md5(khqr_code)
# print("Md5 = ", md5_item)
#
# transaction = khqr.check_payment("98d5ace88069e633880591021bd49dc3")
#
# print("Transaction = ", transaction)