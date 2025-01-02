
from erpnext.accounts.party import get_dashboard_info
import requests
import frappe
import json
from datetime import datetime
from frappe.utils import flt
from frappe.utils import (
	escape_html,
	now
)
from frappe.config import get_modules_from_all_apps

import frappe.utils

from pyfcm import FCMNotification

from frappe import _

import socketio

import base64


# Create a SocketIO client
# sio = socketio.Client()

# Connect to the socket server
# sio.connect('https://testsocket.tuna-erp.com')
# sio.connect('http://localhost:5400')


# @frappe.whitelist(allow_guest=True)
# def emit_message_check():
#     sio.emit("Y2K_sajha_menu", 'Hello from python buddy!')
#     return "done"


# Login

"""
Generate an API secret key for a given user.

Parameters:
- user (str): The username of the user for whom the API secret key is generated.

Returns:
- api_secret (str): The generated API secret key.

Description:
This function generates an API secret key for a given user. It first retrieves the user details using the 'frappe.get_doc' function. Then, it generates a random API secret key using the 'frappe.generate_hash' function. If the user does not have an API key set, it also generates a random API key. The API secret key and API key are then saved in the user's details using the 'user_details.save' function. Finally, the generated API secret key is returned.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.generate_hash' function is used to generate random strings.
- The 'frappe.get_doc' function is used to retrieve user details.
- The 'user_details.save' function is used to save the generated API secret key and API key.
"""
def generate_keys(user):

	user_details = frappe.get_doc("User", user)
	api_secret = frappe.generate_hash(length=15)
	# if api key is not set generate api key
	if not user_details.api_key:
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
	user_details.api_secret = api_secret
	user_details.save(ignore_permissions=True)

	return api_secret

"""
Authenticate a user and generate an API token.

Parameters:
- usr (str): The username of the user.
- pwd (str): The password of the user.

Returns:
- None

Description:
This function authenticates a user by calling the 'frappe.auth.LoginManager.authenticate' method. If the authentication is successful, it generates an API token using the 'generate_keys' function. The API token is then encoded using base64 and stored in the 'token' variable. Finally, the function sets the response message with the authentication details including the API token.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.auth.LoginManager.authenticate' method is used to authenticate the user.
- The 'generate_keys' function is used to generate the API token.
- The API token is encoded using base64.
"""
@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
	try:
		login_manager = frappe.auth.LoginManager()
		login_manager.authenticate(user=usr, pwd=pwd, )
		login_manager.post_login()
	except frappe.exceptions.AuthenticationError:
		print(frappe.exceptions.AuthenticationError)
		frappe.clear_messages()
		frappe.local.response["message"] = {
			"success_key": 0,
			"message": "Authentication Error!"
		}

		return

	api_generate = generate_keys(frappe.session.user)
	user = frappe.get_doc('User', frappe.session.user)

	token = base64.b64encode(
		(f"{user.api_key}:{api_generate}").encode()).decode("utf-8")

	frappe.local.response["message"] = {
		"success_key": 1,
		"message": "Authentication success",
		"sid": frappe.session.sid,
		"token": token,
		"username": user.username,
		"email": user.email,
		"company": user.company,
		"mobile_no": user.mobile_no,
		"full_name": user.full_name,
		"location": user.location,
	}


def is_signup_disabled():
	return frappe.db.get_single_value("Website Settings", "disable_signup", True)


@frappe.whitelist()
def is_walk_in_enable():
	return frappe.db.get_single_value("Sajha Menu Settings", "enable_walk_in_discount")


# push_service = FCMNotification(
# 	api_key="AAAAOmBmb8A:APA91bH6HNgoPBvigMveMSN9HCj7EpQCOPsz5ERnaUeBpND1gT2nRhUZWCzIzlm15ce8kRMr2UGUXkwlTZkjfXsKngagcsbhD8mJ9xTsJltc4-CveOr60nUoYRltMidkIwA_Lg09xRXM")

# Register

"""
Sign up a new user.

Parameters:
- email (str): The email address of the user.
- full_name (str): The full name of the user.
- password (str): The password of the user.
- mobile_no (str): The mobile number of the user.
- location (str): The location of the user.

Returns:
- tuple: A tuple containing the status code and the message.

Description:
This function allows a new user to sign up. It first checks if sign up is disabled by calling the 'is_signup_disabled' function. If sign up is disabled, it raises an exception with the message "Sign Up is disabled".

Next, it checks if a user with the given mobile number already exists. If the user exists and is enabled, it returns a tuple with the status code 0 and the message "Already Registered". If the user exists but is disabled, it returns a tuple with the status code 0 and the message "Registered but disabled".

If the user does not exist, it checks if the number of user creations in the last 60 minutes is greater than 300. If it is, it responds with a web page displaying the message "Too many users signed up recently, so the registration is disabled. Please try back in an hour" and the HTTP status code 429.

If the user creation count is within the limit, it creates a new user document with the given email, full name, password, mobile number, and location. The user is enabled and the password policy is ignored. The user is then inserted into the database.

Next, it checks if a default signup role is set in the Portal Settings. If a default role is set, it adds the role to the user.

Then, it checks if a customer with the given mobile number already exists. If the customer does not exist, it creates a new customer document with the customer name, type, user, mobile number, customer group, and territory. The customer is then inserted into the database.

Finally, it checks if an email was sent to the user. If an email was sent, it returns a tuple with the status code 1 and the message "Please check your email for verification". If no email was sent, it returns a tuple with the status code 2 and the message "Please ask your administrator to verify your sign-up".

Note:
- This function requires the 'frappe' module to be imported.
- The 'is_signup_disabled' function is used to check if sign up is disabled.
- The 'frappe.throw' function is used to raise an exception.
- The 'frappe.db.get' function is used to check if a user with the given mobile number already exists.
- The 'frappe.db.get_creation_count' function is used to check the number of user creations in the last 60 minutes.
- The 'frappe.respond_as_web_page' function is used to respond with a web page.
- The 'frappe.get_doc' function is used to create a new user document and a new customer document.
- The 'user.flags.ignore_permissions' attribute is used to ignore permissions when inserting the user document.
- The 'user.flags.ignore_password_policy' attribute is used to ignore the password policy when inserting the user document.
- The 'user.insert' method is used to insert the user document into the database.
- The 'frappe.db.get_value' function is used to get the default signup role from the Portal Settings.
- The 'user.add_roles' method is used to add the default role to the user.
- The 'frappe.db.get_value' function is used to check if a customer with the given mobile number already exists.
- The 'frappe.get_doc' function is used to create a new customer document.
- The 'customer.insert' method is used to insert the customer document into the database.
- The 'user.flags.email_sent' attribute is used to check if an email was sent to the user.
"""
@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, password, mobile_no, location):
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

	user = frappe.db.get("User", {"mobile_no": mobile_no})
	if user:
		if user.enabled:
			return 0, _("Already Registered")
		else:
			return 0, _("Registered but disabled")
	else:
		if frappe.db.get_creation_count("User", 60) > 300:
			frappe.respond_as_web_page(
				_("Temporarily Disabled"),
				_(
					"Too many users signed up recently, so the registration is disabled. Please try back in an hour"
				),
				http_status_code=429,
			)



		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": escape_html(full_name),
				"enabled": 1,
				"new_password": escape_html(f'{password}'),
				"user_type": "Website User",
				"send_welcome_email": 0,
				'mobile_no': mobile_no,
				'location': location
			}
		)
		user.append('roles',{"doctype": "Has Role","role":"Customer"})
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.insert()

		# set default signup role as per Portal Settings
		default_role = frappe.db.get_value(
			"Portal Settings", None, "default_role")

		if default_role:
			user.add_roles(default_role)



		try:
			companies =  frappe.get_doc("Sync Settings").get("companies")
			payload = {
				'email': email,
				'full_name': full_name,
				'password': escape_html(f'{password}'),
				'mobile_no': mobile_no,
				'location': location
			}

			for company in companies:
				if company.enabled == 1:
					token = base64.b64encode(
							(f"{company.api_key}:{company.api_secret}").encode()).decode("utf-8")
					headers = {'content-type': 'application/json', "Authorization":f'Basic ${token}'}
					r = requests.post('https://'+ company.domain + '/api/method/sajha_menu.api.sign_up_sync', data=json.dumps(payload), headers=headers)
					response_dict = json.loads(r.text)

					pass

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"{e}")


		customerExists = frappe.db.get_value(
			"Customer", {"mobile_number": mobile_no})

		if customerExists == None:
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": escape_html(full_name),
				"type": "Individual",
				"user": email,
				"mobile_number": mobile_no,
				"customer_group": "Commercial",
				"territory": "All Territories"
			})

			customer.insert(ignore_permissions=True, ignore_mandatory=True)

		# if redirect_to:
		#     frappe.cache().hset("redirect_after_login", user.name, redirect_to)

		if user.flags.email_sent:
			return 1, _("Please check your email for verification")
		else:
			return 2, _("Please ask your administrator to verify your sign-up")


@frappe.whitelist(allow_guest=True)
def sign_up_sync():
	data = json.loads(frappe.request.data)
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

	user = frappe.db.get("User", {"mobile_no": data['mobile_no']})
	if user:
		if user.enabled:
			return 0, _("Already Registered")
		else:
			return 0, _("Registered but disabled")
	else:
		if frappe.db.get_creation_count("User", 60) > 300:
			frappe.respond_as_web_page(
				_("Temporarily Disabled"),
				_(
					"Too many users signed up recently, so the registration is disabled. Please try back in an hour"
				),
				http_status_code=429,
			)

		roles = [{'name': 'Customer'}]

		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": data['email'],
				"first_name": escape_html(data['full_name']),
				"enabled": 1,
				"new_password": data['password'],
				"user_type": "Website User",
				"send_welcome_email": 0,
				"roles": roles,
				'mobile_no': data['mobile_no'],
				'location': data['location']
			}
		)
		user.flags.ignore_permissions = True
		user.flags.ignore_password_policy = True
		user.insert()

		# set default signup role as per Portal Settings
		default_role = frappe.db.get_value(
			"Portal Settings", None, "default_role")

		if default_role:
			user.add_roles(default_role)

"""
Edit user profile.

Parameters:
- mobile_no (str): The new mobile number of the user. (optional)
- location (str): The new location of the user. (optional)
- full_name (str): The new full name of the user. (optional)

Returns:
- dict: A dictionary with the key 'success' indicating whether the profile edit was successful or not.

Description:
This function allows the user to edit their profile. It retrieves the user document using the current user's email address. If the 'full_name' parameter is provided, it splits the full name into first name, middle name, and last name. If the 'mobile_no' parameter is provided, it updates the user's mobile number. If the 'location' parameter is provided, it updates the user's location. Finally, it saves the changes to the user document and returns a dictionary with the key 'success' indicating whether the profile edit was successful or not.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.session.data.user' attribute is used to get the current user's email address.
- The 'frappe.get_doc' function is used to retrieve the user document.
- The 'user.first_name', 'user.middle_name', and 'user.last_name' attributes are used to update the user's name.
- The 'user.mobile_no' attribute is used to update the user's mobile number.
- The 'user.location' attribute is used to update the user's location.
- The 'user.save' method is used to save the changes to the user document.
"""
@frappe.whitelist()
def edit_profile(mobile_no='', location='', full_name=''):
	try:
		email = frappe.session.data.user
		user = frappe.get_doc('User', email)
		length = len(full_name.split(' ')) if full_name != '' else 0
		first_name = ''
		middle_name = ''
		last_name = ''
		if length == 1:
			first_name = full_name.split(' ')[0]
		elif length == 2:
			first_name = full_name.split(' ')[0]
			last_name = full_name.split(' ')[1]
		elif length == 3:
			first_name = full_name.split(' ')[0]
			middle_name = full_name.split(' ')[1]
			last_name = full_name.split(' ')[2]
		else:
			first_name = user.first_name
			middle_name = user.middle_name
			last_name = user.last_name
		user.mobile_no = mobile_no if mobile_no != '' else user.mobile_no
		user.location = location if location != '' else user.location
		user.first_name = first_name
		user.middle_name = middle_name
		user.last_name = last_name

		user.save()
		return {'success': True}
	except:
		return {'success': False}


# Get Category

"""
Get category data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the category data.

Description:
This function retrieves the category data for a given company. It first retrieves a list of categories using the 'frappe.get_list' function with a filter on the company name. Then, for each category, it retrieves the category document using the 'frappe.get_doc' function with a filter on the company name. For each subcategory in the category document, it retrieves the subcategory document using the 'frappe.get_doc' function.

Next, it checks if the category already exists in the 'menuData' list. If it does not exist, it appends a new dictionary to the 'menuData' list with the category name, the 'todisplay' flag from the category document, and a list of subcategories. Each subcategory dictionary contains the subcategory name and image from the subcategory document.

If the category already exists in the 'menuData' list, it finds the index of the category in the list using a list comprehension. Then, it appends a new subcategory dictionary to the 'sub_categories' list of the category at the found index.

Finally, it returns the 'menuData' list containing the category data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of categories.
- The 'frappe.get_doc' function is used to retrieve category and subcategory documents.
- The 'filter' parameter is used to filter the category and subcategory documents by the company name.
- The 'menuData' list is used to store the category data.
- The 'next' function is used to find the first item in the 'menuData' list that matches the category name.
- The 'filter' function is used to filter the 'menuData' list by the category name.
- The 'append' method is used to add new dictionaries to the 'menuData' list.
- The 'enumerate' function is used to find the index of the category in the 'menuData' list.
- The 'append' method is used to add new subcategory dictionaries to the 'sub_categories' list.
"""
@frappe.whitelist(allow_guest=True)
def get_category(company):
	menuData = []
	categories = frappe.get_list("Category", filters={"company": company})
	for category in categories:
		doc = frappe.get_doc("Category", category.name,
							 filters={"company": company})
		for subcat in doc.sub_category:
			sub = frappe.get_doc("Sub Category", subcat.sub_category)

			def item_code_check(
				v): return v['category_name'] == subcat.parent
			item = next(filter(item_code_check, menuData), None)

			if item is None:
				menuData.append({"category_name": category.name,
								 "toDisplay": True if doc.todisplay == 1 else False,
								 "sub_categories": [{"subcategory_name": sub.name, "image": sub.image}]})
			else:

				index = next(i for i, x in enumerate(
					menuData) if x['category_name'] == subcat.parent)

				menuData[index]['sub_categories'].append(
					{"subcategory_name": sub.name, "image": sub.image})
	frappe.local.response['data'] = menuData





@frappe.whitelist(allow_guest=True)
def get_category_mobile(company):
	menuData = []
	categories = frappe.get_list("Category", filters={"company": company})
	for category in categories:
		doc = frappe.get_doc("Category", category.name,
							 filters={"company": company})
		if doc.mobile_display == 1:
			for subcat in doc.sub_category:
				sub = frappe.get_doc("Sub Category", subcat.sub_category)
				def item_code_check(
					v): return v['category_name'] == subcat.parent
				item = next(filter(item_code_check, menuData), None)

				if item is None:
					if sub.mobile_display == 1:
						menuData.append({"category_name": category.name,"toDisplay": True, "sub_categories": [{"subcategory_name": sub.name, "image": sub.image}]})
				else:
					if sub.mobile_display == 1:
						index = next(i for i, x in enumerate(
							menuData) if x['category_name'] == subcat.parent)

						menuData[index]['sub_categories'].append(
							{"subcategory_name": sub.name, "image": sub.image})
	frappe.local.response['data'] = menuData

"""
Get menu data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the menu data.

Description:
This function retrieves the menu data for a given company. It first retrieves a list of categories using the 'frappe.get_list' function with a filter on the 'todisplay' flag. For each category, it retrieves the category document using the 'frappe.get_doc' function with a filter on the company name. For each subcategory in the category document, it retrieves the subcategory document using the 'frappe.get_doc' function.

Next, it checks if the category already exists in the 'menuData' list. If it does not exist, it appends a new dictionary to the 'menuData' list with the category name, the 'todisplay' flag from the category document, and a list of subcategories. Each subcategory dictionary contains the subcategory name, image, and item category data obtained from the 'getSubItem' function.

If the category already exists in the 'menuData' list, it finds the index of the category in the list using a list comprehension. Then, it appends a new subcategory dictionary to the 'sub_categories' list of the category at the found index.

Finally, the function sets the 'menuData' list as the response data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of categories.
- The 'frappe.get_doc' function is used to retrieve category and subcategory documents.
- The 'filter' parameter is used to filter the category and subcategory documents by the company name.
- The 'menuData' list is used to store the menu data.
- The 'next' function is used to find the first item in the 'menuData' list that matches the category name.
- The 'filter' function is used to filter the 'menuData' list by the category name.
- The 'append' method is used to add new dictionaries to the 'menuData' list.
- The 'enumerate' function is used to find the index of the category in the 'menuData' list.
- The 'append' method is used to add new subcategory dictionaries to the 'sub_categories' list.
"""
@frappe.whitelist(allow_guest=True)
def getMenu(company):
	menuData = []
	categories = frappe.get_list("Category", {'todisplay': True})
	for category in categories:
		doc = frappe.get_doc("Category", category.name,
							 filters={"company": company})
		for subcat in doc.sub_category:
			sub = frappe.get_doc("Sub Category", subcat.sub_category)

			def item_code_check(v):
				print(v)
				return v['category_name'] == subcat.parent
			item = next(filter(item_code_check, menuData), None)

			if item is None:
				data = getSubItem(sub.name)
				menuData.append({"category_name": category.name,
								"toDisplay": True if doc.todisplay == 1 else False,
								"sub_categories": [{"subcategory_name": sub.name, "image": sub.image, 'item_cateogry': [data]}]})
			else:
				data = getSubItem(sub.name)

				index = next(i for i, x in enumerate(
					menuData) if x['category_name'] == subcat.parent)

				menuData[index]['sub_categories'].append(
					{"subcategory_name": sub.name, "image": sub.image, 'item_cateogry': [data]})
	frappe.local.response['data'] = menuData

"""
Get menu data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the menu data.

Description:
This function retrieves the menu data for a given company. It first retrieves a list of categories using the 'frappe.get_list' function with a filter on the 'todisplay' flag and the company name. For each category, it retrieves the category document using the 'frappe.get_cached_doc' function. It then retrieves the subcategories of the category document and creates a dictionary object for each subcategory. For each subcategory, it retrieves the super subcategories using the 'doc.ssc' attribute and creates a dictionary object for each super subcategory. For each super subcategory, it retrieves the item categories using the 'doc.item_category' attribute and creates a dictionary object for each item category. For each item category, it retrieves the items using the 'doc.items' attribute and creates a dictionary object for each item. Finally, it appends the category dictionary object to the 'menuData' list. The 'menuData' list contains the menu data for the given company.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'frappe.get_list' function is used to retrieve a list of categories.
- The 'frappe.get_cached_doc' function is used to retrieve category, subcategory, super subcategory, item category, and item documents.
- The 'ignore_permissions' parameter is used to ignore permissions when retrieving the documents.
- The 'menuData' list is used to store the menu data.
- The 'categoryObj' dictionary object is used to store the category data.
- The 'subCategoryObj' dictionary object is used to store the subcategory data.
- The 'sscObj' dictionary object is used to store the super subcategory data.
- The 'itemCategoryObj' dictionary object is used to store the item category data.
- The 'itemData' dictionary object is used to store the item data.
- The 'frappe.local.response' dictionary is used to set the 'data' key with the 'menuData' list.
"""
@frappe.whitelist(allow_guest=True)
def get_menu_new(company):
	menuData = []
	categories = frappe.get_list(
		"Category", {'todisplay': True, 'company': company}, ignore_permissions=True)
	for category in categories:
		categoryObj = {}
		doc = frappe.get_cached_doc('Category', category.name)
		sub_categories = doc.sub_category
		categoryObj['category_name'] = category.name
		categoryObj['toDisplay'] = True if doc.todisplay == 1 else False
		categoryObj['sub_categories'] = []
		for sub_cat in sub_categories:
			subCategoryObj = {}
			doc = frappe.get_cached_doc(
				'Sub Category', {'name': sub_cat.sub_category}, ignore_permissions=True)
			subCategoryObj['subcategory_name'] = doc.name
			super_sub_categories = doc.ssc
			subCategoryObj['ssc'] = []
			subCategoryObj['item_cateogry'] = []

			if doc.todisplay == 1:
				categoryObj['sub_categories'].append(subCategoryObj)
			for ssc in super_sub_categories:
				sscObj = {}
				doc = frappe.get_cached_doc("Super Sub Category",
											ssc.ssc_name, ignore_permissions=True)
				sscObj['name'] = doc.name
				item_categories = doc.item_category
				sscObj['item_categories'] = []
				if doc.todisplay == 1:
					subCategoryObj['ssc'].append(sscObj)
				for item_category in item_categories:
					doc = frappe.get_cached_doc(
						'Item Category', item_category.item_category, ignore_permissions=True)
					if doc.todisplay == 1:
						itemCategoryObj = {}
						itemCategoryObj['name'] = doc.name
						items = doc.items
						itemCategoryObj['items'] = []
						# sscObj['item_categories'].append(itemCategoryObj)
						for item in items:
							itemData = {}
							if item.todisplay == 1:
								itemData['name'] = doc.image
								sscObj['item_categories'].append({"items":item, 'image': doc.image})
		menuData.append(categoryObj)
	frappe.local.response['data'] = menuData
	# for sub_category in sub_categories:
	#     sub_cat = frappe.get_doc(
	#         'Sub Category', {'name': sub_category.name})
	#     print(sub_cat)


@frappe.whitelist(allow_guest=True)
def getItems(items):
	print(items)

"""
Get items data.

Parameters:
- items (list): A list of items.

Returns:
- None

Description:
This function prints the items passed as a parameter.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
"""
@frappe.whitelist(allow_guest=True)
def get_subcategory(sub_category):
	subCategory = frappe.get_doc("Sub Category", f"{sub_category}")
	subData = []
	if subCategory.todisplay == 1:
		for ssc in subCategory.ssc:
			sscData = frappe.get_doc("Super Sub Category",
									ssc.ssc_name)
			if sscData.todisplay == 1:
				for item in sscData.item_category:
					itemCat = frappe.get_doc(
						"Item Category", item.item_category)
					if itemCat.todisplay == 1:
						if len(subData) > 0:
							def item_code_check(
								v): return v['super_sub_category'] == sscData.ssc_name
							item = next(filter(item_code_check, subData), None)
							if (item is None):
								subData.append({"sub_category": subCategory.name,
												'super_sub_category': ssc.ssc_name, 'image': sscData.image, 'item_cateogry': [itemCat]})
							else:
								index = next(i for i, x in enumerate(
									subData) if x['super_sub_category'] == sscData.ssc_name)
								subData[index]['item_cateogry'].append(itemCat)

						else:
							subData.append({"sub_category": subCategory.name,
											'super_sub_category': ssc.ssc_name, 'image': sscData.image, 'item_cateogry': [itemCat]})

	frappe.local.response['data'] = subData

@frappe.whitelist(allow_guest=True)
def get_subcategory_mobile(sub_category):
	subCategory = frappe.get_doc("Sub Category", f"{sub_category}")
	subData = []

	if subCategory.mobile_display == 1:
		for ssc in subCategory.ssc:
			sscData = frappe.get_doc("Super Sub Category",
									ssc.ssc_name)
			if sscData.mobile_display == 1:
				for item in sscData.item_category:
					itemCat = frappe.get_doc(
						"Item Category", item.item_category)
					if itemCat.mobile_display == 1:
						if len(subData) > 0:
							def item_code_check(
								v): return v['super_sub_category'] == sscData.ssc_name
							item = next(filter(item_code_check, subData), None)
							if (item is None):
								subData.append({"sub_category": subCategory.name,
												'super_sub_category': ssc.ssc_name, 'image': sscData.image, 'item_cateogry': [itemCat]})
							else:
								index = next(i for i, x in enumerate(
									subData) if x['super_sub_category'] == sscData.ssc_name)
								subData[index]['item_cateogry'].append(itemCat)

						else:
							subData.append({"sub_category": subCategory.name,
											'super_sub_category': ssc.ssc_name, 'image': sscData.image, 'item_cateogry': [itemCat]})

	frappe.local.response['data'] = subData

"""
Get subcategory data for a given subcategory.

Parameters:
- sub_category (str): The name of the subcategory.

Returns:
- list: A list of dictionaries containing the subcategory data.

Description:
This function retrieves the subcategory data for a given subcategory. It first retrieves the subcategory document using the 'frappe.get_doc' function with a filter on the subcategory name.

Next, it checks if the subcategory is set to be displayed. If it is, it iterates over the super subcategories in the subcategory document. For each super subcategory, it retrieves the super subcategory document using the 'frappe.get_doc' function. If the super subcategory is set to be displayed, it iterates over the item categories in the super subcategory document. For each item category, it retrieves the item category document using the 'frappe.get_doc' function. If the item category is set to be displayed, it appends a dictionary to the 'subData' list with the subcategory name, the 'todisplay' flag from the subcategory document, the super subcategory name, the item category name, the 'todisplay' flag from the item category document, the item category image, and the item category ingredients.

If the 'subData' list is not empty, it checks if the super subcategory already exists in the 'subData' list. If it does not exist, it appends a new dictionary to the 'subData' list with the subcategory name, the 'todisplay' flag from the subcategory document, the super subcategory name, and a list of item categories. Each item category dictionary contains the item category name, the 'todisplay' flag from the item category document, the item category image, and the item category ingredients.

If the super subcategory already exists in the 'subData' list, it finds the index of the super subcategory in the list using a list comprehension. Then, it appends a new item category dictionary to the 'items' list of the super subcategory at the found index.

Finally, it returns the 'subData' list containing the subcategory data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the subcategory, super subcategory, and item category documents.
- The 'filter' parameter is used to filter the subcategory document by the subcategory name.
- The 'subData' list is used to store the subcategory data.
- The 'next' function is used to find the first item in the 'subData' list that matches the super subcategory name.
- The 'filter' function is used to filter the 'subData' list by the super subcategory name.
- The 'append' method is used to add new dictionaries to the 'subData' list.
- The 'enumerate' function is used to find the index of the super subcategory in the 'subData' list.
- The 'append' method is used to add new item category dictionaries to the 'items' list.
"""
@frappe.whitelist(allow_guest=True)
def get_subcategoryMobile(sub_category):
	subCategory = frappe.get_doc("Sub Category", f"{sub_category}")
	subData = []
	if subCategory.todisplay == 1:
		for ssc in subCategory.ssc:
			sscData = frappe.get_doc("Super Sub Category",
									ssc.ssc_name)
			if sscData.todisplay == 1:
				for item in sscData.item_category:
					itemCat = frappe.get_doc(
						"Item Category", item.item_category)
					if itemCat.todisplay == 1:
						if len(subData) > 0:
							def item_code_check(
								v): return v['super_sub_category'] == sscData.ssc_name
							item = next(filter(item_code_check, subData), None)
							if (item is None):
								subData.append({"name": subCategory.name,
												"toDisplay": subCategory.todisplay,
												'super_sub_category': [{"name": ssc.ssc_name, 'items': [{"name": itemCat.name, "toDisplay": itemCat.todisplay, 'image': itemCat.image, "ingredients": itemCat.items}]}]})
							else:
								index = next(i for i, x in enumerate(
									subData) if x['super_sub_category'] == sscData.ssc_name)
								subData[index]['super_sub_category']['item_cateogry'].append(
									itemCat)

						else:
							subData.append({"name": subCategory.name, "toDisplay": subCategory.todisplay,
											'super_sub_category': [{"name": ssc.ssc_name, 'items': [{"name": itemCat.name, "toDisplay": itemCat.todisplay, 'image': itemCat.image, "ingredients": itemCat.items}]}]})

	return subData


"""
Get item category data for a given sub category.

Parameters:
- sub_category (str): The name of the sub category.

Returns:
- itemCat (dict): A dictionary containing the item category data.

Description:
This function retrieves the item category data for a given sub category. It first retrieves the sub category document using the 'frappe.get_doc' function. Then, it iterates over the 'ssc' field of the sub category document to retrieve the super sub category document using the 'frappe.get_doc' function. For each super sub category, it checks if the 'todisplay' flag is set to 1. If it is, it iterates over the 'item_category' field of the super sub category document to retrieve the item category document using the 'frappe.get_doc' function. For each item category, it checks if the 'todisplay' flag is set to 1. If it is, it appends a new dictionary to the 'subData' list with the sub category name, super sub category name, image, and item category data. If the 'subData' list is not empty, it checks if an item with the same super sub category name already exists in the list. If it does not exist, it appends a new dictionary to the 'subData' list. Finally, it returns the item category data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the sub category, super sub category, and item category documents.
- The 'subCategory.todisplay' attribute is used to check if the sub category should be displayed.
- The 'sscData.todisplay' attribute is used to check if the super sub category should be displayed.
- The 'itemCat.todisplay' attribute is used to check if the item category should be displayed.
- The 'subData' list is used to store the item category data.
- The 'filter' function is used to filter the 'subData' list by the super sub category name.
- The 'append' method is used to add new dictionaries to the 'subData' list.
- The 'next' function is used to find the first item in the 'subData' list that matches the super sub category name.
- The 'len' function is used to check if the 'subData' list is empty.
"""
@frappe.whitelist(allow_guest=True)
def getSubItem(sub_category):
	subCategory = frappe.get_doc("Sub Category", f"{sub_category}")
	subData = []
	if subCategory.todisplay == 1:
		for ssc in subCategory.ssc:
			sscData = frappe.get_doc("Super Sub Category",
									ssc.ssc_name)
			if sscData.todisplay == 1:
				for item in sscData.item_category:
					itemCat = frappe.get_doc(
						"Item Category", item.item_category)
					if itemCat.todisplay == 1:
						if len(subData) > 0:
							def item_code_check(
								v): return v['super_sub_category'] == sscData.ssc_name
							item = next(filter(item_code_check, subData), None)
							if (item is None):
								subData.append({"sub_category": subCategory.name,
												'super_sub_category': ssc.ssc_name, 'image': sscData.image, 'item_cateogry': [itemCat]})
								return itemCat
							else:
								return itemCat

						else:
							return itemCat

"""
Get item categories for a given subcategory.

Parameters:
- subCategoryName (str): The name of the subcategory.

Returns:
- Returns the document

Description:
This function retrieves the item categories for a given subcategory. It uses the 'frappe.get_list' function to retrieve a list of 'Item Category Child' documents that have the specified subcategory as their parent. The function filters the retrieved documents to include only the 'name' and 'item_category' fields. The resulting list of documents is then assigned to the 'frappe.local.response['data']' variable.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of 'Item Category Child' documents.
- The 'filters' parameter is used to filter the documents by the specified subcategory.
- The 'fields' parameter is used to include only the 'name' and 'item_category' fields in the retrieved documents.
- The 'frappe.local.response['data']' variable is used to store the retrieved documents.
"""
@frappe.whitelist(allow_guest=True)
def get_itemCategory(subCategoryName):
	doc = frappe.get_list("Item Category Child", filters={
		'parent': f"{subCategoryName}"}, fields=['name', 'item_category'])
	frappe.local.response['data'] = doc

# Get Items Category Item

"""
Get items belonging to a specific item category.

Parameters:
- item_category (str): The name of the item category.

Returns:
- list: A list of dictionaries containing the item details.

Description:
This function retrieves items belonging to a specific item category. It uses the 'frappe.get_list' function to query the 'Sub Category Items' table with a filter on the 'parent' field matching the provided item category. The function retrieves the 'name', 'item_code', 'item_name', and 'rate' fields for each item. The item details are then returned as a list of dictionaries.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to query the 'Sub Category Items' table.
- The 'filters' parameter is used to filter the items by the provided item category.
- The 'fields' parameter is used to specify the fields to retrieve for each item.
"""
@frappe.whitelist(allow_guest=True)
def getItemCategoryItems(item_category):
	doc = frappe.get_list("Sub Category Items", filters={
		'parent': f"{item_category}"}, fields=['name', 'item_code', 'item_name', "rate"])
	frappe.local.response['data'] = doc

# Create KOT order
# ROLE: WAITER ONLY

"""
Create a Kitchen Order (KOT) for a table.

Parameters:
- table_name (str): The name of the table for which the KOT is created.
- orderItem (list): A list of items to be included in the KOT.
- company (str): The name of the company.
- kotRemark (str): Any remarks or special instructions for the KOT.

Returns:
- doc (obj): The created Kitchen Orders document.

Description:
This function creates a Kitchen Order (KOT) for a specific table. It first checks the count of existing KOTs for the given company using the 'frappe.db.count' function. If there are existing KOTs, it retrieves the last KOT document using the 'frappe.get_last_doc' function and checks if it was created on a different date than the current date. If it was created on a different date, the KOT ID is set to 1. Otherwise, the KOT ID is incremented by 1.

Next, it retrieves the current date using the 'datetime.now().date()' function.

Then, it creates a new Kitchen Orders document using the 'frappe.get_doc' function with the provided table name, KOT ID, items, company, created date, and remarks. The document is then inserted into the database using the 'doc.insert()' method.

After that, it retrieves the table document using the 'frappe.get_doc' function with the provided table name.

Next, it appends a new 'kot_bot' entry to the 'table' document, containing the ticket number in the format "KOT-{kot_id}" and the name of the created KOT document.

Finally, it saves the changes to the 'table' document using the 'table.save()' method and returns the created Kitchen Orders document.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.count' function is used to count the existing KOTs for the given company.
- The 'frappe.get_last_doc' function is used to retrieve the last KOT document for the given company.
- The 'datetime.now().date()' function is used to get the current date.
- The 'frappe.get_doc' function is used to create a new Kitchen Orders document.
- The 'doc.insert()' method is used to insert the Kitchen Orders document into the database.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'table.append' method is used to add a new 'kot_bot' entry to the table document.
- The 'table.save()' method is used to save the changes to the table document.
"""
def create_kot_order(table_name, orderItem, company, kotRemark):
	try:
		count = frappe.db.count("Kitchen Orders", filters={"company": company})
		if (count > 0):
			last_doc = frappe.get_last_doc(
				"Kitchen Orders", filters={"company": company})
			if last_doc.created_date < datetime.now().date():
				kot_id = 1
			else:
				kot_id = int(last_doc.get("kot_id")) + 1
		else:
			kot_id = 1

		created_date = datetime.now().date()

		doc = frappe.get_doc({"doctype": "Kitchen Orders",
							"table_name": table_name, "kot_id": kot_id, "items": orderItem, "company": company, "created_date": created_date, "remark": kotRemark})
		doc.insert()

		table = frappe.get_doc("Tables", table_name)

		table.append("kot_bot", {
			'ticket_number': f"KOT-{kot_id}",
			'ticket_name': doc.name
		})

		table.save()

		return doc
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")

"""
Get the last Kitchen Order Ticket (KOT) and Bar Order Ticket (BOT) numbers for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- dict: A dictionary containing the last KOT and BOT numbers.

Description:
This function retrieves the last KOT and BOT numbers for a given company. It first counts the number of Kitchen Orders (KOTs) and Bar Orders (BOTs) in the database for the specified company using the 'frappe.db.count' function. If there are KOTs or BOTs present, it retrieves the last document of each type using the 'frappe.get_last_doc' function with a filter on the company name.

For the KOTs, it checks if the created date of the last document is older than the current date. If it is, it sets the KOT number to 1. Otherwise, it increments the KOT number by 1.

For the BOTs, it follows the same logic as for the KOTs.

Finally, it returns a dictionary with the keys 'kotId' and 'botId' containing the last KOT and BOT numbers respectively.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.db.count' function is used to count the number of KOTs and BOTs in the database.
- The 'frappe.get_last_doc' function is used to retrieve the last document of each type.
- The 'datetime.now().date()' expression is used to get the current date.
- The 'int' function is used to convert the KOT and BOT numbers to integers.
"""
@frappe.whitelist()
def getLastKotBotNumber(company):
	kotCount = frappe.db.count("Kitchen Orders", filters={"company": company})
	if (kotCount > 0):
		last_doc = frappe.get_last_doc(
			"Kitchen Orders", filters={"company": company})
		if last_doc.created_date < datetime.now().date():
			kot_id = 1
		else:
			kot_id = int(last_doc.get("kot_id")) + 1
	else:
		kot_id = 1

	barCount = frappe.db.count("Bar Orders", filters={"company": company})
	if (barCount > 0):
		last_doc = frappe.get_last_doc(
			"Bar Orders", filters={"company": company})
		if last_doc.created_date < datetime.now().date():
			bot_id = 1
		else:
			bot_id = int(last_doc.get("bot_id")) + 1
	else:
		bot_id = 1

	frappe.local.response['data'] = {"kotId": kot_id, "botId": bot_id}


"""
Create a bot order.

Parameters:
- table_name (str): The name of the table where the order is placed.
- orderItem (list): A list of items in the order.
- company (str): The name of the company.
- botRemark (str): The remark for the bot order.

Returns:
- doc (obj): The created Bar Orders document.

Description:
This function creates a bot order. It first checks the count of existing Bar Orders for the given company. If there are existing orders, it retrieves the last document and checks if it was created on a different date than the current date. If it was, the bot_id is set to 1. Otherwise, the bot_id is incremented by 1.

Next, it retrieves the current date and creates a new Bar Orders document with the provided table_name, bot_id, items, company, created_date, and remark. The document is then inserted into the database.

Then, it retrieves the Tables document for the given table_name and appends a new kot_bot entry with the ticket_number as "BOT-{bot_id}" and the ticket_name as the name of the created Bar Orders document. The changes are saved to the Tables document.

Finally, the function returns the created Bar Orders document.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.count' function is used to count the number of existing Bar Orders for the given company.
- The 'frappe.get_last_doc' function is used to retrieve the last Bar Orders document for the given company.
- The 'datetime.now().date()' expression is used to get the current date.
- The 'frappe.get_doc' function is used to create a new Bar Orders document.
- The 'doc.insert()' method is used to insert the Bar Orders document into the database.
- The 'frappe.get_doc' function is used to retrieve the Tables document for the given table_name.
- The 'table.append' method is used to add a new kot_bot entry to the Tables document.
- The 'table.save()' method is used to save the changes to the Tables document.
"""
def create_bot_order(table_name, orderItem, company, botRemark):
	try:
		count = frappe.db.count("Bar Orders", filters={"company": company})
		if (count > 0):
			last_doc = frappe.get_last_doc(
				"Bar Orders", filters={"company": company})
			if last_doc.created_date < datetime.now().date():
				bot_id = 1
			else:
				bot_id = int(last_doc.get("bot_id")) + 1
		else:
			bot_id = 1

		created_date = datetime.now().date()

		doc = frappe.get_doc(
			{"doctype": "Bar Orders", "table_name": table_name, "bot_id": bot_id, "items": orderItem, "company": company, 'created_date': created_date, "remark": botRemark})
		doc.insert()

		table = frappe.get_doc("Tables", table_name)
		table.append("kot_bot", {
			'ticket_number': f"BOT-{bot_id}",
			'ticket_name': doc.name
		})

		table.save()

		return doc
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")
"""
Create a Kitchen Order or Bar Order.

Parameters:
- table_name (str): The name of the table.
- orderItem (str): The JSON string representing the order items.
- company (str): The name of the company.
- kotRemark (str, optional): The remark for the Kitchen Order. Defaults to "".
- botRemark (str, optional): The remark for the Bar Order. Defaults to "".
- fromPos (None or str, optional): The source of the order. Defaults to None.

Returns:
- dict or None: If 'fromPos' is None, returns a dictionary containing the 'kot_id' and 'bot_id' of the created orders. If 'fromPos' is not None, returns None.

Description:
This function creates a Kitchen Order or Bar Order based on the type of items in the order. It first separates the order items into food items and bar items based on their category. Then, it calls the 'create_kot_order' function to create a Kitchen Order with the food items, and the 'create_bot_order' function to create a Bar Order with the bar items. The 'kot_id' and 'bot_id' of the created orders are stored in the 'kotid' and 'botid' variables, respectively.

After creating the orders, the function updates the 'current_orders' field of the table to remove any existing orders. Then, it retrieves the 'orders' field of the table and stores it in the 'total_orders' list. The function then iterates over the order items and updates the 'total_orders' list with the quantities of the items. If an item already exists in the 'total_orders' list, its quantity is incremented by the quantity of the new order item. If the item does not exist, a new entry is added to the 'total_orders' list.

Next, the function updates the 'orders' field of the table with the updated 'total_orders' list. It also calculates the total charges for the orders by retrieving the price of each item and multiplying it by the quantity. The total charges are then stored in the 'total_charges' field of the table.

Finally, the function publishes a realtime event to refresh the Kitchen Order and Bar Order screens. If 'fromPos' is None, the function sets the response data with the 'kot_id' and 'bot_id' of the created orders. If 'fromPos' is not None, the function returns None.

Note:
- This function requires the 'frappe' module to be imported.
- The 'create_kot_order' function is used to create a Kitchen Order.
- The 'create_bot_order' function is used to create a Bar Order.
- The 'frappe.publish_realtime' function is used to publish a realtime event.
"""
@frappe.whitelist()
def create_kot_or_bot_order(table_name, orderItem, company, kotRemark="", botRemark="", fromPos=None):
	try:
		orderItem = json.loads(orderItem)
		foodItem = []
		barItem = []
		kotid = 1
		botid = 1

		kot = None
		bot = None

		for item in orderItem:
			sub_item = frappe.db.get_value(
				'Sub Category Items', {'item_code': f"{item['item_code']}"}, ['parent'])
			sub_child = frappe.db.get_value(
				'Item Category Child', {'item_category': sub_item}, ['parent'])
			sub_cat = frappe.db.get_value(
				'Super Sub Category Child', {'ssc_name': sub_child}, ['parent'])

			cat = frappe.db.get_value("Sub Category Child", {
				'sub_category': sub_cat}, ['parent'])
			type = frappe.db.get_value("Category", {'name': cat}, ['type'])

			if type == "Bar":
				barItem.append(item)
			else:
				foodItem.append(item)

		if len(foodItem) > 0:
			kot = create_kot_order(table_name, foodItem, company, kotRemark)
			kotid = kot.kot_id

		if len(barItem) > 0:
			bot = create_bot_order(table_name, barItem, company, botRemark)
			botid = bot.bot_id

		afterSave = frappe.get_doc("Tables", f"{table_name}")
		afterSave.current_orders = []
		afterSave.save()

		# ADD TO TOTAL ORDER OF TABLES
		doc = frappe.get_doc("Tables", f"{table_name}")
		total_orders = []
		for o in doc.orders:
			total_orders.append(
				{'item': o.item, 'quantity': o.quantity})

		for order in orderItem:
			if (len(total_orders) > 0):
				def item_code_check(v):
					return v['item'] == order['item_code']

				item = next(filter(item_code_check, total_orders), None)

				if item is None:
					total_orders.append(
						{'item': order['item_code'], 'quantity': order['quantity']})
				else:

					index = next(i for i, x in enumerate(
						total_orders) if x['item'] == order['item_code'])

					total_orders[index]['quantity'] = total_orders[index]['quantity'] + \
						int(order['quantity'])
			else:
				total_orders.append(
					{'item': order['item_code'], 'quantity': order['quantity']})

		doc.update(
			{
				"orders": []
			}
		)
		doc.save()
		doc.update(
			{
				"orders": total_orders
			}
		)

		doc.save()

		totalCharges = 0.00
		if len(total_orders) > 0:
			for o in total_orders:

				item = frappe.db.get_value("Item Price", {'item_code': o['item'], 'selling': 1}, [
					'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)

				itemCategory = frappe.get_doc(
					"Sub Category Items", {"item_code": o['item']})

				totalCharges = totalCharges + \
					(o['quantity'] * (itemCategory.rate))
			table = frappe.get_doc("Tables", doc.get("name"))
			table.total_charges = totalCharges
			table.db_update()

		else:
			table = frappe.get_doc("Tables", doc.get("name"))
			table.total_charges = 0.00
			table.db_update()

		# topic = str(company).replace(" ", "-").lower()
		# push_service.notify_topic_subscribers(
		#     topic_name=topic, message_title="New Order", message_body=f"Order from {table_name}")

		frappe.publish_realtime('kot_bot_refresh')

		if fromPos == None:
			frappe.local.response['data'] = {
				"kot_id": kotid,
				"bot_id": botid
			}
		else:
			return {"kot": kot, "bot": bot}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")

# Update Kot order Status
# ROLE: COOK ONLY

"""
Update the status of a kitchen order.

Parameters:
- tableId (str): The ID of the kitchen order table.
- status (str): The new status of the kitchen order.

Returns:
- str: returns status field of doc

Description:
This function updates the status of a kitchen order. It retrieves the kitchen order document using the 'frappe.get_doc' function and the provided tableId. It then updates the 'status' field of the document with the provided status. The changes are saved using the 'doc.save' method. Finally, the function sets the 'status' field of the response dictionary in 'frappe.local.response'.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the kitchen order document.
- The 'doc.save' method is used to save the changes to the document.
- The 'frappe.local.response' dictionary is used to set the 'status' field of the response.
"""
def kitchenOrderStatusUpdate(tableId, status):
	doc = frappe.get_doc("Kitchen Orders", f"{tableId}")
	doc.status = f"{status}"
	doc.save()
	frappe.local.response['status'] = doc.status


"""
Create a current order for a table.

Parameters:
- table_name (str): The name of the table.
- orderItem (str): A JSON string representing the order items.
- company (str): The name of the company.

Returns:
- list: A list of dictionaries representing the current order.

Description:
This function creates a current order for a table. It first loads the order items from the JSON string using the 'json.loads' function. Then, it retrieves the table document using the 'frappe.get_doc' function.

Next, it retrieves the current orders from the table document and stores them in the 'current_order' list.

For each order item in the 'orderItem' list, it checks if the item already exists in the 'current_order' list. If it does not exist, it appends the order item to the 'current_order' list. If it exists, it updates the quantity of the existing item.

After updating the 'current_order' list, it updates the 'current_orders' field of the table document with the updated list and saves the document.

If the socket is connected, it emits a table refresh event specific to the company.

Then, it generates a topic name by replacing spaces with hyphens and converting to lowercase. It sends a push notification to the topic subscribers with the message title "New Order" and the message body "Order from {table_name}".

Finally, it returns the 'current_orders' field of the table document.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator with the 'allow_guest=True' parameter is used to allow guest access to the function.
- The 'json.loads' function is used to load the order items from the JSON string.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'doc.current_orders' attribute is used to retrieve the current orders from the table document.
- The 'filter' function is used to find an item in the 'current_order' list based on the item code.
- The 'next' function is used to get the first item in the 'current_order' list that matches the item code.
- The 'enumerate' function is used to get the index of an item in the 'current_order' list.
- The 'doc.update' method is used to update the 'current_orders' field of the table document.
- The 'doc.save' method is used to save the changes to the table document.
- The 'sio.connected' attribute is used to check if the socket is connected.
- The 'sio.emit' method is used to emit a table refresh event specific to the company.
- The 'str.replace' method is used to replace spaces with hyphens in the company name.
- The 'str.lower' method is used to convert the company name to lowercase.
- The 'push_service.notify_topic_subscribers' method is used to send a push notification to the topic subscribers.
"""
@frappe.whitelist(allow_guest=True)
def createCurrentOrder(table_name, orderItem, company):
	orderItem = json.loads(orderItem)
	doc = frappe.get_doc("Tables", f"{table_name}")
	stru = []

	current_order = []
	for current in doc.current_orders:
		current_order.append(
			{'item_code': current.item_code, 'quantity': current.quantity})

	for order in orderItem:
		if (len(current_order) > 0):
			def item_code_check(v):
				return v['item_code'] == order['item_code']

			item = next(filter(item_code_check, current_order), None)

			if item is None:
				current_order.append(order)
			else:
				index = next(i for i, x in enumerate(
					current_order) if x['item_code'] == order['item_code'])

				current_order[index]['quantity'] = current_order[index]['quantity'] + \
					int(order['quantity'])
		else:
			current_order.append(order)

	doc.update(
		{
			"current_orders": current_order
		}
	)
	doc.save()
	# doc.update(
	#     {
	#         "current_orders": current_order
	#     }
	# )
	# doc.save()
	# if sio.connected:
	# 	sio.emit(f'{company}_table_refresh')
	# topic = str(company).replace(" ", "-").lower()
	# push_service.notify_topic_subscribers(
	# 	topic_name=topic, message_title="New Order", message_body=f"Order from {table_name}")

	frappe.local.response['data'] = doc.current_orders


"""
Create a current order for a table in the POS system.

Parameters:
- table_name (str): The name of the table for which the current order is created.
- orderItem (str): A JSON string representing the items and quantities in the current order.
- company (str): The name of the company associated with the current order.

Returns:
- None

Description:
This function creates a current order for a table in the POS system. It first parses the 'orderItem' JSON string into a list of dictionaries representing the items and quantities in the current order. Then, it retrieves the 'Tables' document for the specified table name using the 'frappe.get_doc' function.

The function updates the 'current_orders' field of the 'Tables' document with the new current order. The 'current_orders' field is a list of dictionaries, where each dictionary represents an item in the current order with its item code and quantity.

After updating the 'current_orders' field, the function saves the 'Tables' document. If the connection to the socket server is established, it emits a socket event to refresh the table in the POS system.

Next, the function retrieves the updated 'Tables' document to get the current order. It creates a new list of dictionaries representing the current order, including the item code, name, parent, and quantity of each item.

Finally, the function calls the 'create_kot_or_bot_order' function to create a KOT or BOT order based on the current order. The 'create_kot_or_bot_order' function takes the table name, the JSON string of the current order, the company name, and the 'fromPos' flag as parameters. The 'fromPos' flag is set to True to indicate that the function is called from the POS system.

Note:
- This function requires the 'frappe' module to be imported.
- The 'json.loads' function is used to parse the 'orderItem' JSON string.
- The 'frappe.get_doc' function is used to retrieve the 'Tables' document.
- The 'doc.update' method is used to update the 'current_orders' field of the 'Tables' document.
- The 'doc.save' method is used to save the 'Tables' document.
- The 'sio.emit' method is used to emit a socket event to refresh the table in the POS system.
- The 'create_kot_or_bot_order' function is called to create a KOT or BOT order based on the current order.
"""
@frappe.whitelist(allow_guest=True)
def createCurrentOrderPOS(table_name, orderItem, company):
	orderItem = json.loads(orderItem)
	doc = frappe.get_doc("Tables", f"{table_name}")
	current_order = []
	for current in orderItem:
		current_order.append(
			{'item_code': current['item_code'], 'quantity': current['quantity']})

	# doc.db_update()

	doc.update(
		{
			"current_orders": current_order
		}
	)
	doc.save()
	orders = frappe.get_doc("Tables", table_name)
	new_order = []
	for curr in orders.current_orders:
		new_order.append({
			"item_code": curr.item_code,
			"name": curr.name,
			"parent": curr.parent,
			# "parentfield": "current_orders",
			# "parenttype": "Tables",
			"quantity": curr.quantity
		})

	# print(new_order)
	data = create_kot_or_bot_order(
		table_name, json.dumps(new_order), company, fromPos=True)

	frappe.local.response['data'] = data

"""
Get tables data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the tables data.

Description:
This function retrieves the tables data for a given company. It uses the 'frappe.get_list' function to retrieve a list of tables with the specified company name. The fields included in the result are 'name', 'company', and 'category'. The function returns the retrieved tables data as a list of dictionaries.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve the tables data.
- The 'filters' parameter is used to filter the tables by the company name.
- The 'fields' parameter is used to specify the fields to include in the result.
"""
@frappe.whitelist(allow_guest=True)
def getTables(company):
	doc = frappe.get_list("Tables", filters={'company': company}, fields=[
		'name', 'company', 'category'])
	frappe.local.response['tables'] = doc

"""
Get the rate and tax information for a given item.

Parameters:
- itemCode (str): The code of the item.

Returns:
- dict: A dictionary containing the item name, price list rate, and tax rate.

Description:
This function retrieves the rate and tax information for a given item. It first retrieves the item details from the "Item Price" table using the 'frappe.db.get_value' function. The item details include the item name, item code, and price list rate.

Next, it retrieves the tax template for the item from the "Item" table using the 'frappe.get_doc' function. If the item has taxes associated with it, it retrieves the tax rate from the "Item Tax Template Detail" table using the 'frappe.get_doc' function.

Finally, it returns a dictionary with the item name, price list rate, and tax rate.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_value' function is used to retrieve the item details from the "Item Price" table.
- The 'frappe.get_doc' function is used to retrieve the tax template and tax rate from the "Item" and "Item Tax Template Detail" tables.
- The 'itemTax.taxes' attribute is used to check if the item has taxes associated with it.
- The 'dataTax.get' method is used to retrieve the tax rate from the "Item Tax Template Detail" table.
"""
@frappe.whitelist()
def getItemRate(itemCode):
	try:
		item = frappe.db.get_value("Item Price", {'item_code': itemCode, 'selling': 1}, [
			'name', 'item_name', 'item_code', 'price_list_rate'], as_dict=1)
		itemTax = frappe.get_doc("Item", itemCode)
		taxTemplate = None
		rate = 0.0
		if len(itemTax.taxes) > 0:
			taxTemplate = itemTax.taxes[0].item_tax_template

			dataTax = frappe.get_doc("Item Tax Template Detail", {
				"parent": f"{taxTemplate}"})
			rate = dataTax.get("tax_rate")
		return {'item_name': item['item_name'], "item": item['price_list_rate'], "rate": rate/100}
	except Exception as e:
		print(e)
		return e

"""
Get the tax rate for a given item.

Parameters:
- itemCode (str): The code of the item.

Returns:
- float: The tax rate for the item, expressed as a decimal.

Description:
This function retrieves the tax rate for a given item. It first retrieves the item document using the 'frappe.get_doc' function. If the item has taxes associated with it, it retrieves the tax template from the first tax in the item's taxes list. Then, it retrieves the tax rate from the 'Item Tax Template Detail' document associated with the tax template. Finally, it returns the tax rate divided by 100.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the item document and the 'Item Tax Template Detail' document.
- The 'itemTax.taxes' attribute is used to check if the item has taxes associated with it.
- The 'itemTax.taxes[0].item_tax_template' attribute is used to retrieve the tax template from the first tax in the item's taxes list.
- The 'frappe.get_doc' function is used to retrieve the 'Item Tax Template Detail' document associated with the tax template.
- The 'dataTax.get("tax_rate")' expression is used to retrieve the tax rate from the 'Item Tax Template Detail' document.
- The tax rate is returned as a decimal by dividing it by 100.
"""
@frappe.whitelist()
def getTaxRate(itemCode):
	itemTax = frappe.get_doc("Item", itemCode)
	taxTemplate = None
	rate = 0.0
	if len(itemTax.taxes) > 0:
		taxTemplate = itemTax.taxes[0].item_tax_template

		dataTax = frappe.get_doc("Item Tax Template Detail", {
			"parent": f"{taxTemplate}"})
		rate = dataTax.get("tax_rate")
	return rate/100

"""
Clear the current order of a table.

Parameters:
- table_name (str): The name of the table.

Returns:
- bool: True if the current order is cleared successfully, False otherwise.

Description:
This function clears the current order of a table. It retrieves the table document using the 'frappe.get_doc' function with the provided table name. Then, it sets the 'current_order' attribute of the table document to an empty list and saves the changes using the 'table.save' method. Finally, it returns True if the current order is cleared successfully, and False otherwise.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'table.current_order' attribute is used to access the current order of the table.
- The 'table.save' method is used to save the changes to the table document.
"""
@frappe.whitelist()
def clearTable(table_name):
	table = frappe.get_doc("Tables", f"{table_name}")
	table.current_order = []
	table.save()
	return True

"""
Get all tables for a given company and outlet.

Parameters:
- company (str): The name of the company.
- outlet (str): The name of the outlet.

Returns:
- list: A list of dictionaries containing the table data.

Description:
This function retrieves all tables for a given company and outlet. It first retrieves a list of tables using the 'frappe.get_list' function with filters on the company and outlet names. The tables are ordered by name in ascending order.

For each table, the function retrieves the category from the 'Tables' document using the 'frappe.db.get_value' function. It also retrieves the 'Tables' document itself using the 'frappe.get_doc' function.

The function then updates each table dictionary with additional information. It sets the 'current_orders' key to the number of current orders associated with the table. It sets the 'billable_orders' key to the number of billable orders associated with the table. It sets the 'enabled' key to the value of the 'enabled' attribute in the 'Tables' document. It sets the 'category' key to the retrieved category.

Finally, the function returns the list of tables with the updated information.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of tables.
- The 'frappe.db.get_value' function is used to retrieve the category from the 'Tables' document.
- The 'frappe.get_doc' function is used to retrieve the 'Tables' document.
- The 'len' function is used to get the number of current orders and billable orders.
"""
@frappe.whitelist(allow_guest=True)
def getAllTables(company, outlet):
	tables = frappe.get_list(
		"Tables", filters={'company': company, "restaurant_names": outlet}, order_by="name".format('asc'))
	for table in tables:
		category = frappe.db.get_value("Tables", table['name'], "category")
		# current_orders = frappe.get_list('Current Orders', filters={
		#     'parent': table['name']})

		doc = frappe.get_doc("Tables", table['name'])
		# print(doc.orders)
		# billable_orders = frappe.get_list(
		#     'Total Order', filters={'parent': table['name']})
		table['current_orders'] = len(doc.current_orders)
		table['billable_orders'] = len(doc.orders)
		table['enabled'] = doc.enabled
		table['category'] = category,
		table['table_name'] = doc.tab_name
	return tables

"""
Get waiter table data.

Returns:
- list: A list of dictionaries containing the waiter table data.

Description:
This function retrieves the waiter table data for the current user. It first retrieves the waiter profile document using the current user's email address. Then, for each table in the waiter profile, it retrieves the category and enabled status of the table from the Tables document. If the table is enabled, it retrieves the full table document using the table name and enabled status. Finally, it appends a dictionary to the 'tableData' list containing the table name, the number of current orders, the number of billable orders, the outlet name, and the category.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.session.user' attribute is used to get the current user's email address.
- The 'frappe.get_doc' function is used to retrieve the waiter profile document and the table document.
- The 'frappe.db.get_value' function is used to retrieve the category and enabled status of the table.
- The 'tableData' list is used to store the waiter table data.
- The 'append' method is used to add new dictionaries to the 'tableData' list.
"""
@frappe.whitelist()
def getWaiterTable():
	user = frappe.session.user

	waiterProfile = frappe.get_doc("Waiter Profile", user)

	tableData = []

	for table in waiterProfile.tables:
		category = frappe.db.get_value("Tables", table.table_name, "category")
		enabled = frappe.db.get_value("Tables", table.table_name, "enabled")

		if enabled == True:
			doc = frappe.get_doc(
				"Tables", {"name": table.table_name, "enabled": 1})
			tableData.append({
				"name": doc.get("name"),
				"current_orders": len(doc.current_orders),
				"billable_orders": len(doc.orders),
				"outlet": doc.restaurant_names,
				"category": category
			})

	return tableData

"""
Get the outlet assigned to the current waiter.

Returns:
- str: The name of the outlet assigned to the current waiter.

Description:
This function retrieves the outlet assigned to the current waiter. It first gets the current user's email address using the 'frappe.session.user' attribute. Then, it uses the 'frappe.db.get_value' function to get the value of the 'outlet' field from the 'Waiter Profile' document for the current user. Finally, it returns the name of the outlet.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.session.user' attribute is used to get the current user's email address.
- The 'frappe.db.get_value' function is used to get the value of the 'outlet' field from the 'Waiter Profile' document.
"""
@frappe.whitelist()
def getWaiterOutlet():
	user = frappe.session.user
	outlet = frappe.db.get_value("Waiter Profile", user, "outlet")
	frappe.local.response['data'] = outlet

"""
Get the menu items for a given outlet.

Parameters:
- outlet (str): The name of the outlet.

Returns:
- list: A list of menu item names.

Description:
This function retrieves the menu items for a given outlet. It first retrieves the 'Restaurant names' document for the specified outlet using the 'frappe.get_doc' function. Then, it iterates over the 'menu' field of the document and appends the 'item_category' of each menu item to the 'menu_item_name' list.

Finally, it returns the 'menu_item_name' list containing the menu item names.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the 'Restaurant names' document.
- The 'menu' field of the document contains the menu items.
- The 'item_category' field of each menu item is appended to the 'menu_item_name' list.
"""
@frappe.whitelist()
def get_outlet_menu(outlet):
	restro_menu = frappe.get_doc("Restaurant names", outlet)
	menu_item_name = []
	for item in restro_menu.menu:
		menu_item_name.append(item.item_category)

	frappe.local.response['data'] = menu_item_name

"""
Get table details.

Parameters:
- table (str): The name of the table.

Returns:
- dict: A dictionary containing the table details.

Description:
This function retrieves the details of a table. It first retrieves the table document using the 'frappe.get_doc' function. Then, for each order in the table, it retrieves the item details using the 'frappe.db.get_value' function and the 'frappe.get_doc' function. It also retrieves the tax template details using the 'frappe.get_doc' function.

Next, it checks if the item has any taxes. If it does, it retrieves the tax rate from the tax template details.

Finally, it appends the order details to the 'orders' list and returns a dictionary containing the merged table name, the list of orders, the total charges, and the count of KOT BOT.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'frappe.get_doc' function is used to retrieve the table document, item document, subcategory items document, and item tax template detail document.
- The 'frappe.db.get_value' function is used to retrieve the item price details.
- The 'table.orders' attribute is used to iterate over the orders in the table.
- The 'itemTax.taxes' attribute is used to check if the item has any taxes.
- The 'orders.append' method is used to add the order details to the 'orders' list.
- The 'len' function is used to calculate the count of KOT BOT.
"""
@frappe.whitelist(allow_guest=True)
def getTableDetails(table):
	table = frappe.get_doc("Tables", table)
	orders = []
	for order in table.orders:
		item = frappe.db.get_value("Item", order.item, ['name', 'item_code', 'item_name'], as_dict=1)
		itemTax = frappe.get_doc("Item", order.item)
		itemCategory = frappe.get_doc(
			"Sub Category Items", {"item_code": order.item})
		taxTemplate = None
		rate = 0.0
		if len(itemTax.taxes) > 0:
			taxTemplate = itemTax.taxes[0].item_tax_template

			dataTax = frappe.get_doc("Item Tax Template Detail", {
				"parent": f"{taxTemplate}"})
			rate = dataTax.get("tax_rate")

		orders.append({'item': {"item_code": item['item_code'], "name": item['name'], 'item_name': item['item_name'], 'price_list_rate': (
			itemCategory.rate)}, 'qty': order.quantity,'original_qty': order.quantity, 'taxRate': rate})
	# return table

	return {'mergedTable': f"{table.merged_tables}", 'orders': orders, 'total': table.total_charges, 'kbcount': len(table.kot_bot)}

"""
Get table details for a given table.

Parameters:
- table (str): The name of the table.

Returns:
- list: A list of dictionaries containing the table details.

Description:
This function retrieves the details of a given table. It first retrieves the table document using the 'frappe.get_doc' function. Then, for each item in the table's current orders, it retrieves the corresponding subcategory item, item category child, super sub category child, sub category child, category, and item name using the 'frappe.db.get_value' function.

Next, it appends a new dictionary to the 'current_orders' list with the item code, item ID, item name, quantity, and category.

Finally, it returns the 'current_orders' list containing the table details.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'frappe.db.get_value' function is used to retrieve the subcategory item, item category child, super sub category child, sub category child, category, and item name.
- The 'current_orders' list is used to store the table details.
- The 'append' method is used to add new dictionaries to the 'current_orders' list.
"""
@frappe.whitelist(allow_guest=True)
def getTableDetailsMobile(table):
	table = frappe.get_doc("Tables", table)

	current_orders = []

	for item in table.current_orders:

		sub_item = frappe.db.get_value(
			'Sub Category Items', {'item_code': f"{item.item_code}"}, ['parent'])
		sub_child = frappe.db.get_value(
			'Item Category Child', {'item_category': sub_item}, ['parent'])
		sub_cat = frappe.db.get_value(
			'Super Sub Category Child', {'ssc_name': sub_child}, ['parent'])

		cat = frappe.db.get_value("Sub Category Child", {
			'sub_category': sub_cat}, ['parent'])
		type = frappe.db.get_value("Category", {'name': cat}, ['type'])
		item_name = frappe.db.get_value("Item", item.item_code, "item_name")

		current_orders.append({
			'item_code': item.item_code,
			"id": item.name,
			"item_name": item_name,
			"quantity": item.quantity,
			"category": type
		})

	frappe.local.response['current_orders'] = current_orders


"""
Create a sales invoice based on the provided document.

Parameters:
- doc (str): A JSON string representing the document.

Returns:
- str: The name of the created sales invoice.

Description:
This function creates a sales invoice based on the provided document. The document is first parsed from JSON format using the 'json.loads' function. If the document has a 'name' field, it checks if a single draft invoice exists based on the 'Sajha Menu Settings' configuration. If a single draft invoice exists, it raises an exception with a message containing a link to the existing draft invoice.

Next, it retrieves the necessary data from the document, such as the orders, order items, and KOT bot. It also retrieves the table and company information.

For each order item, it retrieves the item details, item tax details, item category, and tax template. It then adds the order item to the 'orders' list.

A new sales invoice document is created using the 'frappe.new_doc' function. The customer, table name, due date, and update stock fields are set. The default taxes and charges, default income account, and default cost center are also set.

The sales charges are added to the sales invoice based on the company's VAT account.

The naming series for the sales invoice is set based on the restaurant name associated with the table.

The KOT bot items are added to the sales invoice.

For each order item in the 'orders' list, a sales invoice item is created and added to the sales invoice. The item code, item name, description, rate, amount, uom, quantity, item tax template, and cost center are set. The income account is set based on the item's default income account or the default income account of the company.

The sales invoice is then inserted into the database, ignoring permissions, links, duplicates, and mandatory fields.

After the sales invoice is created, the table's total charges, orders, and KOT bot are reset and saved.

Finally, the name of the created sales invoice is returned.

Note:
- This function requires the 'frappe' module to be imported.
- The 'json.loads' function is used to parse the document from JSON format.
- The 'frappe.db.get_single_value' function is used to check if a single draft invoice exists.
- The 'frappe.throw' function is used to raise an exception with a message containing a link to the existing draft invoice.
- The 'frappe.get_doc' function is used to retrieve the table and company documents.
- The 'frappe.new_doc' function is used to create a new sales invoice document.
- The 'sales_invoice.append' method is used to add sales charges and KOT bot items to the sales invoice.
- The 'sales_invoice.append' method is used to add sales invoice items to the sales invoice.
- The 'sales_invoice.insert' method is used to insert the sales invoice into the database.
- The 'table.save' method is used to save the changes to the table document.
"""
@frappe.whitelist()
def createSalesInvoice(doc):
	try:
		doc = json.loads(doc)
		if doc.get("name"):
			single_draft = frappe.db.get_single_value(
				"Sajha Menu Settings", "single_draft")

			if single_draft == True:
				inv = frappe.db.get_list("Sales Invoice", {"docstatus": 0})
				if len(inv) > 0:
					frappe.throw(
						f"Please submit draft invoice <a target='__blank' href='/app/sales-invoice/{inv[0].name}'>{inv[0].name}</a>")
					return {"code": "DRA_EXISTS", "name": inv[0].name}
			orders = []
			orderItems = doc['orders']
			kot_bot = doc['kot_bot']

			table = frappe.get_doc("Tables", doc.get('name'))

			company = doc['company']

			for o in orderItems:
				item = frappe.db.get_value("Item Price", {'item_code': o['item'], 'selling': 1}, [
					'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
				itemtax = frappe.get_doc("Item", o['item'])

				itemCategory = frappe.get_doc(
					"Sub Category Items", {"item_code": o['item']})

				taxTemplate = None
				if len(itemtax.taxes) > 0:
					taxTemplate = itemtax.taxes[0].item_tax_template
				orders.append({
					'item_code': item['item_code'],
					'item_name': item['item_name'],
					'qty': o['quantity'],
					'rate': itemCategory.rate,
					'amount': o['quantity'] * (itemCategory.rate),
					'uom': item['uom'],
					"description": "Test Description",
					'tax_template': taxTemplate
				})

			sales_invoice = frappe.new_doc('Sales Invoice')
			sales_invoice.customer = "Sajha Customer"
			sales_invoice.table_name = doc.get("name")
			sales_invoice.due_date = frappe.utils.nowdate()
			sales_invoice.update_stock = 1

			default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
				"company": doc.get('company'), "is_default": 1})
			default_incm_account = frappe.db.get_value(
				"Company", {"name": doc.get("company")}, ['default_income_account'])
			default_cost_center = frappe.db.get_value(
				"Company", {"name": doc.get("company")}, ['cost_center'])

			sales_invoice.taxes_and_charges = default_taxes_and_charges

			company = frappe.get_doc("Company", doc.get('company'))

			sales_charges = sales_invoice.append('taxes', {})
			sales_charges.charge_type = "On Net Total"
			sales_charges.account_head = f"VAT - {company.abbr}"

			restaurantName = frappe.get_doc(
				"Restaurant names", table.get("restaurant_names"))
			sales_invoice.naming_series = restaurantName.naming_series

			for ko in kot_bot:
				kot_bot_itm = sales_invoice.append("kot_bot", {})
				kot_bot_itm.ticket_number = ko['ticket_number']
				kot_bot_itm.ticket_name = ko['ticket_name']

			for o in orders:
				print(o)
				if o['qty'] > 0:
					default_account = None
					itemAccount = frappe.get_doc("Item", o['item_code'])
					for itm in itemAccount.item_defaults:
						if doc.get('company') == itm.company:
							default_account = itm.income_account
							break
					sales_invoice_itm = sales_invoice.append('items', {})
					sales_invoice_itm.item_code = o['item_code']
					sales_invoice_itm.item_name = o['item_name']
					sales_invoice_itm.description = o['description']
					sales_invoice_itm.rate = o['rate']
					sales_invoice_itm.amount = o['amount']
					sales_invoice_itm.uom = o['uom']
					sales_invoice_itm.qty = o['qty']
					if o['tax_template'] != None:
						sales_invoice_itm.item_tax_template = o['tax_template']
					sales_invoice_itm.cost_center = default_cost_center
					if default_account != None:
						sales_invoice_itm.income_account = default_account
					else:
						sales_invoice_itm.income_account = default_incm_account

			sales_invoice.insert(ignore_permissions=True, ignore_links=True,
								ignore_if_duplicate=True, ignore_mandatory=True)

			table.total_charges = 0.0
			table.orders = []
			table.kot_bot = []
			table.save()
			return sales_invoice.name
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")


@frappe.whitelist()
def clearDumpDataSalesInvoiceBeforeSave(doc, event):
	doc.dump_data = ""
	pass


"""
Disable or enable a menu item.

Parameters:
- doc (object): The document object representing the menu item.
- event (str): The event that triggered the function.

Returns:
- None

Description:
This function disables or enables a menu item based on the value of the 'disabled' field in the document object. If the 'disabled' field is set to 1, the function retrieves a list of subcategory items associated with the menu item using the 'frappe.db.get_list' function. For each subcategory item, it sets the 'todisplay' field to 0 using the 'frappe.db.set_value' function. If the 'disabled' field is set to 0, the function retrieves the list of subcategory items and sets the 'todisplay' field to 1. Finally, the changes are committed to the database using the 'frappe.db.commit' function.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'doc' parameter represents the menu item document.
- The 'event' parameter represents the event that triggered the function.
- The 'frappe.db.get_list' function is used to retrieve a list of subcategory items associated with the menu item.
- The 'frappe.db.set_value' function is used to set the value of the 'todisplay' field for each subcategory item.
- The 'frappe.db.commit' function is used to commit the changes to the database.
"""
@frappe.whitelist()
def disable_menu_item(doc,event):
	if doc.disabled == 1:
		menu_item_list = frappe.db.get_list("Sub Category Items", {'item_code': doc.item_code},['name','item_code'], ignore_permissions=True)
		for item in menu_item_list:
			frappe.db.set_value("Sub Category Items",{'item_code': item.item_code}, 'todisplay', 0)
			frappe.db.commit()
	elif doc.disabled == 0:
		menu_item_list = frappe.db.get_list("Sub Category Items", {'item_code': doc.item_code},['name','item_code'], ignore_permissions=True)
		for item in menu_item_list:
			frappe.db.set_value("Sub Category Items",{'item_code': item.item_code}, 'todisplay', 1)
			frappe.db.commit()
	pass

"""
Clear the orders of a table after saving.

Parameters:
- doc (frappe.model.document.Document): The document being saved.
- event (str): The event triggering the save.

Returns:
- None

Description:
This function clears the orders of a table after saving the document. It first checks if the 'table_name' attribute of the document is not None. If it is not None, it retrieves the 'Tables' document using the 'frappe.get_doc' function. Then, it checks if the 'split_bill' attribute of the 'Tables' document is not 1. If it is not 1, it clears the 'orders' attribute of the 'Tables' document and saves the changes.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called via the Frappe API.
- The 'frappe.get_doc' function is used to retrieve the 'Tables' document.
- The 'data.orders' attribute is used to clear the orders of the table.
- The 'data.save' method is used to save the changes to the 'Tables' document.
"""
@frappe.whitelist()
def clearTableOrderAfterSaveSave(doc, event):
	if (doc.table_name != None):
		data = frappe.get_doc("Tables", doc.table_name)
		if data.split_bill != 1:
			data.orders = []
			data.save()
	pass

"""
Check if the current user has the required roles to stop or remove an item.

Returns:
- bool: True if the user has the required roles, False otherwise.

Description:
This function checks if the current user has the required roles to stop or remove an item. It first retrieves the current user using the 'frappe.session.user' attribute. Then, it retrieves the roles of the user using the 'frappe.get_roles' function.

The required roles are defined as ['Administrator', 'Restaurant Manager']. The function iterates over each role in the required roles list. If a role is found in the user's roles, the 'returnValue' variable is set to False. If a role is not found, the 'returnValue' variable is set to True and the function returns immediately.

Finally, the function returns the 'returnValue' variable, which indicates whether the user has the required roles or not.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.session.user' attribute is used to retrieve the current user.
- The 'frappe.get_roles' function is used to retrieve the roles of the user.
"""
@frappe.whitelist()
def stopremove():
	user = frappe.session.user
	roles = frappe.get_roles(user)

	required_roles = ['Administrator', 'Restaurant Manager']
	returnValue = False

	for role in required_roles:
		if role in roles:
			returnValue = False
			return returnValue
		else:
			returnValue = True

	return returnValue


@frappe.whitelist()
def stopCancel():
	user = frappe.session.user
	roles = frappe.get_roles(user)

	required_roles = ['Administrator', 'Tuna Kot']
	returnValue = False

	for role in required_roles:
		if role in roles:
			returnValue = False
			return returnValue
		else:
			returnValue = True

	return returnValue


"""
Get current orders for a given table.

Parameters:
- table (str): The name of the table.

Returns:
- list: A list of dictionaries containing the current orders.

Description:
This function retrieves the current orders for a given table. It first retrieves the table document using the 'frappe.get_doc' function. Then, for each current order in the table's 'current_orders' field, it calls the 'getItemRate' function to get the item details. The item details include the item name, quantity, and rate.

Next, it appends a new dictionary to the 'currentOrders' list with the product code, item name, quantity, and rate.

Finally, it returns the 'currentOrders' list containing the current orders.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'getItemRate' function is used to get the item details.
- The 'currentOrders' list is used to store the current orders.
- The 'append' method is used to add new dictionaries to the 'currentOrders' list.
"""
@frappe.whitelist()
def getCurrentOrders(table):
	table = frappe.get_doc("Tables", f"{table}")
	currentOrders = []
	for current in table.current_orders:

		item = getItemRate(current.item_code)

		currentOrders.append({'product': current.item_code, 'name': item['item_name'],
							'quantity': current.quantity, 'rate': item['item']})
	return currentOrders


"""
Move an order to a room folio.

Parameters:
- company (str): The name of the company.
- table (str): The name of the table.
- orderItems (str): A JSON string representing the order items.
- room (str): The room number.
- split_customer (str): The name of the customer for split billing. (optional)
- discount_value (float): The discount value. (optional)

Returns:
- sales_invoice (Sales Invoice): The created sales invoice.

Description:
This function moves an order to a room folio. It first parses the order items from the JSON string. Then, it retrieves the room folio with the specified status, company, and room number. If no room folio is found, it sets the response data to 'No room folio found' and returns.

If a table is specified, it retrieves the table document and gets the 'kot_bot' field. It then creates a list of orders with the necessary details from the order items. The necessary details include the item code, item name, quantity, rate, amount, unit of measure, income account, description, and tax template.

Next, it creates a new sales invoice document and sets the customer, table name, due date, company, discount amount, and update stock fields. It also sets the default taxes and charges, default income account, and default cost center. The naming series is set based on the restaurant name.

For each kot_bot item, it appends a new kot_bot item to the sales invoice.

It appends the sales charges for VAT to the sales invoice.

For each order, it retrieves the default income account from the item document and appends a new item to the sales invoice. It sets the item code, item name, rate, amount, description, unit of measure, quantity, tax template, and cost center. If a default income account is not found, it uses the default income account from the company document.

The sales invoice is then inserted, submitted, and saved to the room folio. The table orders, kot_bot, and total charges are cleared and saved. If the socket is connected, it emits a table refresh event.

Finally, the sales invoice is returned.

Note:
- This function requires the 'frappe' module to be imported.
- The 'json.loads' function is used to parse the order items from the JSON string.
- The 'frappe.db.get_list' function is used to retrieve the room folio with the specified filters.
- The 'frappe.get_doc' function is used to retrieve the table document and the room folio document.
- The 'frappe.new_doc' function is used to create a new sales invoice document.
- The 'sales_invoice.append' method is used to append items to the sales invoice.
- The 'frappe.db.get_value' function is used to retrieve the default taxes and charges, default income account, and default cost center.
- The 'frappe.get_traceback' function is used to get the traceback in case of an exception.
- The 'frappe.log_error' function is used to log the error.
"""
@frappe.whitelist()
def moveToRoomFolio(company, table, orderItems, room, split_customer, discount_value):
	module_exists = "Tuna HMS" in get_modules_from_all_apps()
	if module_exists:
		try:
			orderItems = json.loads(orderItems)
			todayDate = now()

			room_folio_list = frappe.db.get_list('Room Folio HMS', filters={'status': [
				'=', 'Checked In'], 'check_in': [ '<=', todayDate],'check_out': ['>=', todayDate], 'company': ['like', company], 'room_no': ['=', room]})

			if (len(room_folio_list) == 0):
				frappe.local.response['data'] = 'No room folio found.'
				return
			roomFolio = frappe.get_doc("Room Folio HMS", room_folio_list[0])

			if table:
				table = frappe.get_doc("Tables", table)
				kot_bot = table.get('kot_bot')
				testDoc = frappe.db.get_value("KOT_BOT",{'ticket_name':table.kot_bot[0].ticket_name, 'parenttype': "Sales Invoice"}, "parent")
				if testDoc is not None:
					return {"code": "ALREADY_EXISTS", 'invoice': testDoc}
				orders = []
				for o in orderItems:
					item = frappe.db.get_value("Item Price", {'item_code': o['item_code'], 'selling': 1}, [
						'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
					itemTax = frappe.get_doc("Item", o["item_code"])
					taxTemplate = None
					itemCategory = frappe.get_doc(
						"Sub Category Items", {"item_code": o['item_code']})
					if len(itemTax.taxes) > 0:
						taxTemplate = itemTax.taxes[0].item_tax_template
					orders.append({
						'item_code': item['item_code'],
						'item_name': item['item_name'],
						'qty': o['quantity'],
						'rate': flt(itemCategory.rate),
						'amount': flt((o['quantity'] * itemCategory.rate)),
						'uom': item['uom'],
						'income_account': "Entertainment Expenses - Y",
						"description": "Test Description",
						'bill_item': o['bill_item'] if "bill_item" in o else item['item_name'],
						"tax_template": taxTemplate
					})

				sales_order = frappe.new_doc("Sales Order")
				sales_order.customer = "Sajha Customer" if roomFolio.customer == None else roomFolio.customer
				if table.get("merged_tables") == None or table.get("merged_tables") == "":
					sales_order.table_name = table.get("name")
				else:
					sales_order.table_name = f"{table.get('name')},{table.get('merged_tables')}"
				sales_order.due_date = frappe.utils.nowdate()
				sales_order.company = company
				sales_order.apply_discount_on = "Net Total"
				sales_order.status = "Closed"
				sales_order.discount_amount = discount_value
				default_incm_account = frappe.db.get_value(
					"Company", {"name": company}, ['default_income_account'])
				default_cost_center = frappe.db.get_value(
					"Company", {"name": company}, ['cost_center'])

				default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
					"company": company, "is_default": 1})

				sales_order.taxes_and_charges = default_taxes_and_charges
				company_sales = frappe.get_doc("Company", company)

				sales_charges = sales_order.append('taxes', {})
				sales_charges.charge_type = "On Net Total"
				sales_charges.account_head = f"VAT - {company_sales.abbr}"
				kot_bot = table.get("kot_bot")
				for ko in kot_bot:
					kot_bot_itm = sales_order.append("kot_bot", {})
					kot_bot_itm.ticket_number = ko.ticket_number
					kot_bot_itm.ticket_name = ko.ticket_name
				for o in orders:
					default_account = None
					itemAccount = frappe.get_doc("Item", o['item_code'])
					for itm in itemAccount.item_defaults:
						if company == itm.company:
							default_account = itm.income_account
							break
					sales_order_itm = sales_order.append('items', {})
					sales_order_itm.item_code = o['item_code']
					sales_order_itm.item_name = o['item_name']
					sales_order_itm.rate = o['rate']
					sales_order_itm.delivery_date = frappe.utils.nowdate()
					sales_order_itm.amount = o['amount']
					sales_order_itm.description = o['description']
					sales_order_itm.uom = o['uom']
					sales_order_itm.qty = o['qty']
					if o['tax_template']:
						sales_order_itm.item_tax_template = o['tax_template']
					sales_order_itm.cost_center = default_cost_center
					if default_account != None:
						sales_order_itm.income_account = default_account
					else:
						sales_order_itm.income_account = default_incm_account

				sales_order.insert()
				sales_order.submit()

				sales_invoice = frappe.new_doc('Sales Invoice')
				if roomFolio.split_bill == 1:
					sales_invoice.customer = split_customer
				else:
					sales_invoice.customer = roomFolio.customer
				sales_invoice.table_name = table.get('name')
				sales_invoice.due_date = frappe.utils.nowdate()
				sales_invoice.company = company
				sales_invoice.apply_discount_on = "Net Total"
				sales_invoice.discount_amount = discount_value
				sales_invoice.update_stock = 1

				default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
					"company": table.get("company"), "is_default": 1})
				default_incm_account = frappe.db.get_value(
					"Company", {"name": company}, ['default_income_account'])
				default_cost_center = frappe.db.get_value(
					"Company", {"name": company}, ['cost_center'])

				sales_invoice.taxes_and_charges = default_taxes_and_charges

				company = frappe.get_doc("Company", table.get('company'))

				restaurantName = frappe.get_doc(
					"Restaurant names", table.get("restaurant_names"))
				sales_invoice.naming_series = restaurantName.naming_series

				for ko in kot_bot:
					kot_bot_itm = sales_invoice.append("kot_bot", {})
					kot_bot_itm.ticket_number = ko.ticket_number
					kot_bot_itm.ticket_name = ko.ticket_name


				sales_charges = sales_invoice.append('taxes', {})
				sales_charges.charge_type = "On Net Total"
				sales_charges.account_head = f"VAT - {company.abbr}"

				for o in orders:
					default_account = None
					itemAccount = frappe.get_doc("Item", o['item_code'])
					for itm in itemAccount.item_defaults:
						if company.get('name') == itm.company:
							default_account = itm.income_account
							break
					sales_invoice_itm = sales_invoice.append('items', {})
					sales_invoice_itm.item_code = o['item_code']
					sales_invoice_itm.item_name = o['item_name']
					sales_invoice_itm.rate = o['rate']
					sales_invoice_itm.amount = o['amount']
					sales_invoice_itm.description = o['description']
					sales_invoice_itm.uom = o['uom']
					sales_invoice_itm.qty = o['qty']
					sales_invoice_itm.bill_item_name = o['bill_item']
					if o['tax_template']:
						sales_invoice_itm.item_tax_template = o['tax_template']
					sales_invoice_itm.cost_center = default_cost_center
					if default_account != None:
						sales_invoice_itm.income_account = default_account
					else:
						sales_invoice_itm.income_account = default_incm_account

				sales_invoice.insert()
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"{e}")
			raise
		try:
			sales_invoice.submit()
			frappe.db.set_value('Sales Order', sales_order.get('name'), 'sales_invoice_reference', sales_invoice.get('name'))
			roomFolioInvoice = roomFolio.append('restrurant_invoice', {})

			roomFolioInvoice.reference = sales_invoice.name

			roomFolio.save()

			table.orders = []
			table.kot_bot = []
			table.total_charges = 0.0
			table.merged_tables = None
			table.save()
			return sales_invoice
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"{e}")
	else:
		pass
"""
Update stock entry for a given quantity, default warehouse, item code, company, and stock entry type.

Parameters:
- qty_to_update (float): The quantity to update in the stock entry.
- default_warehouse (str): The default warehouse for the stock entry.
- itemCode (str): The item code for the stock entry.
- company (str): The name of the company.
- stock_entry_type (str, optional): The type of stock entry. Defaults to "Material Issue".

Returns:
- None

Description:
This function updates the stock entry for a given quantity, default warehouse, item code, company, and stock entry type. It first checks the stock entry type and assigns the appropriate warehouse variable. Then, it retrieves the initial 'is_stock_item' value from the 'Item' document using the 'frappe.get_value' function.

If the initial 'is_stock_item' value is True, it creates a new stock entry document using the 'frappe.new_doc' function. It sets the company and stock entry type for the new stock entry document. Then, it appends a new item to the 'items' field of the stock entry document with the item code, warehouse, quantity to update, and 'allow_zero_valuation_rate' flag. Finally, it inserts and submits the new stock entry document.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_value' function is used to retrieve the initial 'is_stock_item' value from the 'Item' document.
- The 'frappe.new_doc' function is used to create a new stock entry document.
- The 'new_stock_entry.company' attribute is used to set the company for the new stock entry document.
- The 'new_stock_entry.stock_entry_type' attribute is used to set the stock entry type for the new stock entry document.
- The 'new_stock_entry.append' method is used to add a new item to the 'items' field of the stock entry document.
- The 'new_stock_entry.insert' method is used to insert the new stock entry document into the database.
- The 'new_stock_entry.submit' method is used to submit the new stock entry document.
"""
def stock_entry_update(qty_to_update, default_warehouse,itemCode,company, stock_entry_type="Material Issue"):
	if stock_entry_type == "Material Issue":
		warehouse = "s_warehouse"
	else:
		warehouse = "t_warehouse"
	initial_is_stock_item = frappe.get_value(
		"Item", itemCode, "is_stock_item")

	if  initial_is_stock_item:
		new_stock_entry = frappe.new_doc(
			"Stock Entry")
		new_stock_entry.company = company
		new_stock_entry.stock_entry_type = stock_entry_type
		new_stock_entry.append("items", {
			"item_code": itemCode,
			warehouse: default_warehouse,
			"qty": qty_to_update,
			"allow_zero_valuation_rate": 1
		})
		new_stock_entry.insert()
		new_stock_entry.submit()

"""
Create a sales invoice for a point of sale transaction.

Parameters:
- company (str): The name of the company.
- customer (str): The name of the customer.
- writeOffAmount (float): The write-off amount for the invoice.
- discount_value (float): The discount amount for the invoice.
- payment_type (str): The type of payment for the invoice.
- table (str): The name of the table.
- orderItems (str): The JSON string representing the order items.
- paid_amount (float): The amount paid for the invoice.
- payment_mode (str): The mode of payment for the invoice.
- reference_no (str): The reference number for the payment.
- reference_date (str): The reference date for the payment.
- guest_name (str): The name of the guest.
- pax (int): The number of guests.
- invoice_remark (str): The remark for the invoice.
- draft (bool): Indicates whether the invoice is a draft or not.
- transaction_date (str): The transaction date for the invoice.

Returns:
- invoice_name (str): The name of the created sales invoice.

Description:
This function creates a sales invoice for a point of sale transaction. It first retrieves the company details using the 'frappe.get_doc' function. If the payment mode is 'foc' (free of charge), it checks the stock availability for each order item and returns an error message if any item is out of stock. It then updates the stock quantity for each order item using the 'stock_entry_update' function. Next, it creates a new journal entry with the necessary accounting entries for the invoice. The journal entry is then saved and submitted. If the payment mode is not 'foc', it checks if a single draft sales invoice already exists and returns an error message if it does. It then retrieves the table details using the 'frappe.get_doc' function. It creates a list of order items with their details and creates a new sales invoice with the necessary details. The sales invoice is then saved and submitted. If the 'draft' parameter is set to False, it creates a payment entry for the invoice and saves it. Finally, if the socket connection is active, it emits a table refresh event. The name of the created sales invoice is returned.

Note:
- This function requires the following modules to be imported: frappe, json, datetime, frappe.utils, frappe.permissions, pyfcm, socketio, base64.
- The 'frappe.get_doc' function is used to retrieve document details.
- The 'frappe.new_doc' function is used to create a new document.
- The 'frappe.db.get_value' function is used to retrieve values from the database.
- The 'frappe.utils.nowdate' function is used to get the current date.
- The 'datetime.strptime' function is used to parse a date string.
- The 'flt' function is used to convert a value to a float.
- The 'sales_invoice.append' function is used to append child documents to the sales invoice.
- The 'sales_invoice.insert' function is used to save the sales invoice.
- The 'sales_invoice.submit' function is used to submit the sales invoice.
- The 'payment_entry.append' function is used to append child documents to the payment entry.
- The 'payment_entry.insert' function is used to save the payment entry.
- The 'payment_entry.submit' function is used to submit the payment entry.
- The 'sio.connected' attribute is used to check if the socket connection is active.
- The 'sio.emit' function is used to emit a socket event.
"""
@frappe.whitelist()
def createSalesInvoicePOS(company, customer,multi_payment, createLateSales, writeOffAmount, discount_value, table,split, orderItems, paid_amount, payment_mode, guest_name, pax, invoice_remark, draft, transaction_date):
	try:
		logs = frappe.new_doc("Request Logs Sajha")
		logs.title = "Sajha Menu"
		logs.request = json.dumps({
	  				'company':company,
					'customer':customer,
	 				'multi_payment':json.loads(multi_payment),
					'writeOffAmount':writeOffAmount,
					'discount_value':discount_value,
					'table':table,
	 				'orderItems':json.loads(orderItems),
					'paid_amount':paid_amount,
					'payment_mode':payment_mode,
					'guest_name':guest_name,
					'pax':pax,
					'invoice_remark':invoice_remark,
					'draft':draft,
					'split': split,
					'transaction_date':transaction_date
	 			})
		logs.insert(ignore_permissions=True)
		frappe.db.savepoint("pos_invoice")
		create_sales_order = frappe.db.get_single_value(
			"Sajha Menu Settings", "sales_order")
		orderItems = json.loads(orderItems)
		companyData = frappe.get_doc("Company", company)
		if payment_mode == "foc":
			table = frappe.get_doc("Tables", table)
			for o in orderItems:
				initial_is_stock_item = frappe.get_value(
					"Item", o['item_code'], "is_stock_item")
				if initial_is_stock_item:
					binStock = frappe.db.get_value("Bin", {"item_code": o['item_code']}, "actual_qty")
					if binStock == None:
						frappe.local.response['message'] = f"Stock not available for <strong>{o['item_code']}</strong>"
						return
					elif binStock <= 0:
						frappe.local.response['message'] = f"Stock not available for <strong>{o['item_code']}</strong>"
						return

			for o in orderItems:
				default_warehouse = frappe.db.get_value('Item Default', {'parent': o['item_code'], 'company': company}, 'default_warehouse')
				stock_entry_update(o['quantity'],default_warehouse,o['item_code'],company)

			doc = frappe.new_doc("Journal Entry")
			doc.voucher_type = "Journal Entry"
			doc.company = company
			doc.posting_date = datetime.now().date()
			doc.user_remark = invoice_remark
			doc.foc = 1
			doc.percent = companyData.foc_restro_percent

			kot_bot = table.get("kot_bot")
			for ko in kot_bot:
				kot_bot_itm = doc.append("kot_bot", {})
				kot_bot_itm.ticket_number = ko.ticket_number
				kot_bot_itm.ticket_name = ko.ticket_name

			accounting_entries_itm = doc.append('accounts', {})
			accounting_entries_itm.account = companyData.foc_restro_dr_account
			accounting_entries_itm.party_type = "Customer"
			accounting_entries_itm.party = customer
			accounting_entries_itm.debit_in_account_currency = paid_amount * (companyData.foc_restro_percent/100)
			accounting_entries_itm.credit_in_account_currency = 0.0

			accounting_entries_itm = doc.append('accounts', {})
			accounting_entries_itm.account = companyData.foc_restro_cr_account
			accounting_entries_itm.credit_in_account_currency = paid_amount * (companyData.foc_restro_percent/100)
			accounting_entries_itm.debit_in_account_currency = 0.0

			doc.insert()
			doc.submit()


			table.orders = []
			table.kot_bot = []
			table.total_charges = 0.0
			table.merged_tables = None
			table.save()
			frappe.db.commit()
			frappe.local.response['message'] = "Done"
			return

		single_draft = frappe.db.get_single_value(
			"Sajha Menu Settings", "single_draft")

		if single_draft == True:
			inv = frappe.db.get_list("Sales Invoice", {"docstatus": 0})
			if len(inv) > 0:
				return {"code": "DRA_EXISTS", "name": inv[0].name}

		if table:
			table = frappe.get_doc("Tables", table)
			doc = frappe.db.get_value("KOT_BOT",{'ticket_name':table.kot_bot[0].ticket_name, 'parenttype': "Sales Invoice"}, "is_split")
			if doc is not None and doc == False:
				return {"code": "ALREADY_EXISTS", 'invoice': doc}

			orders = []

			for o in orderItems:
				item = frappe.db.get_value("Item Price", {'item_code': o['item_code'], 'selling': 1}, [
					'name', 'item_code', 'price_list_rate', 'item_name', 'uom',], as_dict=True)
				itemTax = frappe.get_doc("Item", o["item_code"])
				itemCategory = frappe.get_doc(
					"Sub Category Items", {"item_code": o['item_code']})
				taxTemplate = None
				if len(itemTax.taxes) > 0:
					taxTemplate = itemTax.taxes[0].item_tax_template
				orders.append({
					'item_code': item['item_code'],
					'item_name': item['item_name'],
					'qty': flt(o['quantity']),
					'rate': flt(itemCategory.rate),
					'amount': flt(flt(o['quantity']) * (itemCategory.rate)),
					'uom': item['uom'],
					'bill_item': o['bill_item'] if "bill_item" in o else item['item_name'],
					'income_account': "Entertainment Expenses - Y",
					"description": "Test Description",
					"tax_template": taxTemplate
				})
			# If creating sales order is enabled in sajha menu settings
			if create_sales_order:
				sales_order = frappe.new_doc("Sales Order")
				sales_order.customer = "Sajha Customer" if customer == None else customer
				if table.get("merged_tables") == None or table.get("merged_tables") == "":
					sales_order.table_name = table.get("name")
				else:
					sales_order.table_name = f"{table.get('name')},{table.get('merged_tables')}"
				sales_order.due_date = frappe.utils.nowdate()
				sales_order.company = company
				sales_order.apply_discount_on = "Net Total"
				sales_order.status = "Closed"
				sales_order.discount_amount = discount_value
				default_incm_account = frappe.db.get_value(
					"Company", {"name": company}, ['default_income_account'])
				default_cost_center = frappe.db.get_value(
					"Company", {"name": company}, ['cost_center'])

				default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
					"company": company, "is_default": 1})

				sales_order.taxes_and_charges = default_taxes_and_charges
				sales_order.write_off_amount = writeOffAmount
				company_sales = frappe.get_doc("Company", company)

				sales_charges = sales_order.append('taxes', {})
				sales_charges.charge_type = "On Net Total"
				sales_charges.account_head = f"VAT - {company_sales.abbr}"
				kot_bot = table.get("kot_bot")

				for ko in kot_bot:
					kot_bot_itm = sales_order.append("kot_bot", {})
					kot_bot_itm.ticket_number = ko.ticket_number
					kot_bot_itm.ticket_name = ko.ticket_name
					kot_bot_itm.is_split = split
				for o in orders:
					default_account = None
					itemAccount = frappe.get_doc("Item", o['item_code'])
					for itm in itemAccount.item_defaults:
						if company == itm.company:
							default_account = itm.income_account
							break
					sales_order_itm = sales_order.append('items', {})
					sales_order_itm.item_code = o['item_code']
					sales_order_itm.item_name = o['item_name']
					sales_order_itm.rate = o['rate']
					sales_order_itm.delivery_date = frappe.utils.nowdate()
					sales_order_itm.amount = o['amount']
					sales_order_itm.description = o['description']
					sales_order_itm.uom = o['uom']
					sales_order_itm.qty = o['qty']
					if o['tax_template']:
						sales_order_itm.item_tax_template = o['tax_template']
					sales_order_itm.cost_center = default_cost_center
					if default_account != None:
						sales_order_itm.income_account = default_account
					else:
						sales_order_itm.income_account = default_incm_account

				sales_order.insert()
				sales_order.submit()

			if createLateSales == False:
				sales_invoice = frappe.new_doc('Sales Invoice')
				sales_invoice.customer = "Sajha Customer" if customer == None else customer
				if table.get("merged_tables") == None or table.get("merged_tables") == "":
					sales_invoice.table_name = table.get("name")
				else:
					sales_invoice.table_name = f"{table.get('name')},{table.get('merged_tables')}"
				sales_invoice.due_date = frappe.utils.nowdate()

				sales_invoice.company = company
				sales_invoice.apply_discount_on = "Net Total"
				sales_invoice.is_split = split
				sales_invoice.discount_amount = discount_value
				if guest_name != None:
					sales_invoice.guest_name = guest_name
				sales_invoice.pax = pax if pax != None else 1
				sales_invoice.update_stock = 1
				default_incm_account = frappe.db.get_value(
					"Company", {"name": company}, ['default_income_account'])
				default_cost_center = frappe.db.get_value(
					"Company", {"name": company}, ['cost_center'])

				default_taxes_and_charges = frappe.db.get_value("Sales Taxes and Charges Template", {
					"company": company, "is_default": 1})

				sales_invoice.taxes_and_charges = default_taxes_and_charges
				sales_invoice.write_off_amount = writeOffAmount
				sales_invoice.write_off_account = frappe.db.get_value(
					"Company", {"name": company}, 'write_off_account')
				sales_invoice.write_off_cost_center = frappe.db.get_value(
					"Company", {"name": company}, 'round_off_cost_center')
				# sales_invoice.write_off_outstanding_amount_automatically = 1

				if transaction_date != "":
					sales_invoice.transaction_date = datetime.strptime(
						transaction_date, "%Y-%m-%d")
				else:
					sales_invoice.transaction_date = datetime.date(datetime.now())
				company = frappe.get_doc("Company", company)

				sales_charges = sales_invoice.append('taxes', {})
				sales_charges.charge_type = "On Net Total"
				sales_charges.account_head = f"VAT - {company.abbr}"

				restaurantName = frappe.get_doc(
					"Restaurant names", table.get("restaurant_names"))
				sales_invoice.naming_series = restaurantName.naming_series
				sales_invoice.invoice_remarks = invoice_remark

				kot_bot = table.get("kot_bot")

				for ko in kot_bot:
					kot_bot_itm = sales_invoice.append("kot_bot", {})
					kot_bot_itm.ticket_number = ko.ticket_number
					kot_bot_itm.ticket_name = ko.ticket_name
					kot_bot_itm.is_split = split
				for o in orders:
					default_account = None
					itemAccount = frappe.get_doc("Item", o['item_code'])
					for itm in itemAccount.item_defaults:
						if company == itm.company:
							default_account = itm.income_account
							break
					sales_invoice_itm = sales_invoice.append('items', {})
					sales_invoice_itm.item_code = o['item_code']
					sales_invoice_itm.item_name = o['item_name']
					sales_invoice_itm.bill_item_name = o['bill_item']
					sales_invoice_itm.rate = o['rate']
					sales_invoice_itm.amount = o['amount']
					sales_invoice_itm.description = o['description']
					sales_invoice_itm.uom = o['uom']
					sales_invoice_itm.qty = o['qty']
					if o['tax_template']:
						sales_invoice_itm.item_tax_template = o['tax_template']
					sales_invoice_itm.cost_center = default_cost_center
					if default_account != None:
						sales_invoice_itm.income_account = default_account
					else:
						sales_invoice_itm.income_account = default_incm_account

				sales_invoice.insert()

	except Exception as e:
		frappe.db.savepoint(save_point="pos_invoice")
		frappe.log_error(frappe.get_traceback(), f"{e}")
		raise

	try:
		if draft == False and createLateSales == False:
			sales_invoice.submit()

		if draft == False and createLateSales == False:
			if payment_mode != "credit":
				multi_payment = json.loads(multi_payment)
				for pay in multi_payment:
					default_cash_account = None
					mode_of_payment = frappe.get_cached_doc(
						"Mode of Payment", pay['name'], ignore_permissions=True)
					if (len(mode_of_payment.accounts) > 0):
						for payment in mode_of_payment.accounts:
							if (company.get("name") == payment.company):
								default_cash_account = payment.default_account
								break

					if default_cash_account == None:

						default_cash_account = frappe.db.get_value(
							"Company", {"name": company.get("name")}, ['default_cash_account']) if pay['type'] == 'Cash' else frappe.db.get_value(
							"Company", {"name": company.get("name")}, ['default_bank_account'])
					sales = frappe.get_doc("Sales Invoice", sales_invoice.name)
					payment_entry = frappe.new_doc("Payment Entry")
					payment_entry.party_type = "Customer"
					payment_entry.party = sales_invoice.get("customer")
					payment_entry.payment_type = "Receive"
					payment_entry.mode_of_payment = pay['name']
					payment_entry.posting_date = frappe.utils.today()
					payment_entry.paid_to = default_cash_account
					payment_entry.received_amount = flt(pay['amount']) if flt(pay['amount']) < sales.get(
						"outstanding_amount") else sales.get("outstanding_amount")
					payment_entry.paid_amount = flt(pay['amount']) if flt(pay['amount']) < sales.get(
						"outstanding_amount") else sales.get("outstanding_amount")
					payment_entry.company = company.name
					# payment_entry.paid_from_account_currency = "NPR"
					# payment_entry.paid_to_account_currency = "NPR"
					if pay['type'] != "Cash":
						payment_entry.reference_no = pay['reference_no']
						payment_entry.reference_date = pay['reference_date']

					payment_entry_reference = payment_entry.append(
						'references', {})
					payment_entry_reference.reference_doctype = "Sales Invoice"
					payment_entry_reference.reference_name = sales_invoice.name
					payment_entry_reference.total_amount = sales.get(
						"grand_total")
					payment_entry_reference.allocated_amount = flt(pay['amount']) if flt(pay['amount']) < sales.get(
						"outstanding_amount") else sales.get("outstanding_amount")
					payment_entry_reference.due_date = frappe.utils.today()

					payment_entry.insert()
					payment_entry.submit()
	except Exception as e:
		frappe.db.savepoint(save_point="pos_invoice")
		frappe.log_error(frappe.get_traceback(), f"{e}")
		raise

	if split == True and createLateSales == False:
		for ord in orders:
			index = next(i for i, x in enumerate(
				table.orders) if x.item == ord['item_code'])

			if index >= -1:
				table.orders[index].quantity = table.orders[index].quantity - ord['qty']
				if table.orders[index].quantity == 0:
					table.orders.pop(index)
			if len(table.orders) == 0:
				table.orders = []
				table.kot_bot = []
				table.total_charges = 0.0
				table.merged_tables = None
		table.save()
	else:
		table.orders = []
		table.kot_bot = []
		table.total_charges = 0.0
		table.merged_tables = None
		table.save()
	frappe.db.commit()
	if createLateSales == False:
		return sales_invoice.name
	elif create_sales_order == True:
		return sales_order.name
	else:
		return True



@frappe.whitelist()
def clearTablePOS(table):
		table = frappe.get_doc("Tables", table)
		doc = frappe.db.get_value("KOT_BOT",{'ticket_name':table.kot_bot[0].ticket_name, 'parenttype': "Sales Invoice"}, "parent")
		is_split = frappe.db.get_value("Sales Invoice", doc, "is_split")
		table_name = frappe.db.get_value("Sales Invoice", doc, "table_name")
		if doc is None or (is_split and table.get('name') == table_name):
			return {"code": "NO_INVOICE_FOUND"}
		else:
			table.orders = []
			table.kot_bot = []
			table.total_charges = 0.0
			table.merged_tables = None
			table.save()
			return {"code": "SUCCESS"}


"""
Get occupied rooms for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the occupied room data.

Description:
This function retrieves the occupied rooms for a given company. It first retrieves a list of rooms using the 'frappe.get_list' function with filters on the room status ('Occupied') and company name. For each room, it retrieves the room folio list using the 'frappe.db.get_list' function with filters on the room status ('Checked In') and room number. It then retrieves the room folio document using the 'frappe.get_doc' function with the first room folio from the room folio list. The room folio document is added to the room dictionary as the 'roomFolio' key. Finally, the function returns the list of rooms.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of rooms.
- The 'frappe.db.get_list' function is used to retrieve a list of room folios.
- The 'frappe.get_doc' function is used to retrieve the room folio document.
- The 'filters' parameter is used to filter the rooms and room folios by status and company name.
- The 'room' dictionary is used to store the room data.
- The 'roomFolio' key is used to store the room folio document.
"""
@frappe.whitelist()
def getOccupiedRooms(company):
	module_exists = "Tuna HMS" in get_modules_from_all_apps()
	if module_exists:
		rooms = frappe.get_list(
			'Room HMS', filters={'status': 'Occupied', 'company': company})
		for room in rooms:
			room_folio_list = frappe.db.get_list('Room Folio HMS', filters={'status': [
				'=', 'Checked In'], 'room_no': ['=', room.name]})
			room['roomFolio'] = frappe.get_doc(
				"Room Folio HMS", room_folio_list[0])
		return rooms
	else:
		pass

"""
Get room folio data for a given room.

Parameters:
- room (str): The room number for which the folio data is retrieved.

Returns:
- str: The customer name associated with the room folio.

Description:
This function retrieves the room folio data for a given room. It first retrieves a list of room folios from the 'Room Folio HMS' table using the 'frappe.db.get_list' function. The room folios are filtered based on the status being 'Checked In' and the room number matching the provided room parameter.

Next, it retrieves the room folio document using the 'frappe.get_doc' function with the first room folio from the retrieved list.

If the 'split_bill' attribute of the room folio document is set to 1, indicating a split bill, the function returns the 'split_bill_customer' attribute of the room folio document. Otherwise, it returns the 'customer' attribute of the room folio document.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.db.get_list' function is used to retrieve a list of room folios.
- The 'filters' parameter is used to filter the room folios based on the status and room number.
- The 'frappe.get_doc' function is used to retrieve the room folio document.
- The 'room_folio_list[0]' is used to access the first room folio from the retrieved list.
- The 'split_bill' attribute of the room folio document is used to determine if the bill is split.
- The 'split_bill_customer' attribute of the room folio document is used to retrieve the customer name for a split bill.
- The 'customer' attribute of the room folio document is used to retrieve the customer name for a non-split bill.
"""
@frappe.whitelist()
def getRoomFolioData(room):
	module_exists = "Tuna HMS" in get_modules_from_all_apps()
	if module_exists:
		room_folio_list = frappe.db.get_list('Room Folio HMS', filters={'status': [
			'=', 'Checked In'], 'room_no': ['=', room]})
		roomFolio = frappe.get_doc("Room Folio HMS", room_folio_list[0])

		if roomFolio.split_bill == 1:
			return roomFolio.split_bill_customer
		else:
			return roomFolio.customer


"""
Get user room details.

Parameters:
- customer (str): The name of the customer.

Returns:
- dict: A dictionary containing the customer name and a list of room numbers.

Description:
This function retrieves the room details for a given customer. It first retrieves a list of room folio documents using the 'frappe.get_list' function with filters on the customer name and status. For each room folio document, it retrieves the room folio document using the 'frappe.get_doc' function. It then appends the room number to the 'rooms' list in the 'item' dictionary.

Finally, it returns the 'item' dictionary containing the customer name and the list of room numbers.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of room folio documents.
- The 'frappe.get_doc' function is used to retrieve room folio documents.
- The 'item' dictionary is used to store the customer name and room numbers.
- The 'item['customerName']' attribute is used to store the customer name.
- The 'item['rooms']' attribute is used to store the list of room numbers.
"""
@frappe.whitelist()
def getUserRoomDetail(customer):
	module_exists = "Tuna HMS" in get_modules_from_all_apps()
	if module_exists:
		doc = frappe.get_list(doctype="Room Folio HMS", filters={
			"customer": customer, "status": "Checked In"})
		item = {"customerName": "", "rooms": []}
		item['customerName'] = customer
		for room in doc:
			data = frappe.get_doc("Room Folio HMS", room.name)
			item['rooms'].append(data.room_no)
		return item

"""
Get take order data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the take order data.

Description:
This function retrieves the take order data for a given company. It first retrieves a list of categories using the 'frappe.get_list' function with filters on the company name and the 'todisplay' flag. For each category, it retrieves a list of subcategories using the 'frappe.db.get_list' function with a filter on the parent category name.

Next, for each subcategory, it calls the 'get_subcategoryMobile' function to retrieve the subcategory data. The subcategory data is then appended to the 'data' list as a dictionary with the category name and the subcategory data.

Finally, it returns the 'data' list containing the take order data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of categories.
- The 'frappe.db.get_list' function is used to retrieve a list of subcategories.
- The 'get_subcategoryMobile' function is used to retrieve the subcategory data.
- The 'data' list is used to store the take order data.
"""
@frappe.whitelist(allow_guest=True)
def getTakeOrder(company):
	data = []
	categoryList = frappe.get_list(
		"Category", filters={"company": company, "todisplay": 1})
	for category in categoryList:
		subCategoryList = frappe.db.get_list(
			"Sub Category Child", {"parent": category.name}, ['name', 'sub_category'], ignore_permissions=True)

		for sub in subCategoryList:
			sc = get_subcategoryMobile(sub.sub_category)
			data.append({
				"category": category.name,
				"sub_category": sc
			})

	frappe.local.response["data"] = data

"""
Update the current order for a given table.

Parameters:
- table (str): The name of the table.
- currentOrders (str): A JSON string representing the current orders.

Returns:
- None

Description:
This function updates the current order for a given table. It first converts the 'currentOrders' parameter from a JSON string to a Python list of dictionaries. Each dictionary represents an item in the current order and contains the 'item_code' and 'quantity' keys.

Next, it retrieves the table document using the 'frappe.get_doc' function with the table name as the parameter.

Then, it clears the 'current_orders' field of the table document by updating it with an empty list.

After that, it saves the changes to the table document.

Next, it updates the 'current_orders' field of the table document with the new current order.

Then, it saves the changes to the table document again.

If the socket.io client is connected, it emits a table refresh event specific to the company of the table.

Finally, it sets the response status to "OK".

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'json.loads' function is used to convert the 'currentOrders' parameter from a JSON string to a Python list.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'upTable.update' method is used to update the 'current_orders' field of the table document.
- The 'upTable.save' method is used to save the changes to the table document.
- The 'sio.connected' attribute is used to check if the socket.io client is connected.
- The 'sio.emit' method is used to emit a table refresh event specific to the company of the table.
- The 'frappe.local.response' dictionary is used to set the response status.
"""
@frappe.whitelist(allow_guest=True)
def updateCurrentOrder(table, currentOrders):
	curr_order = []
	currentOrders = json.loads(currentOrders)
	for co in currentOrders:
		curr_order.append({
			"item_code": co['item_code'],
			"quantity": co['quantity']
		})
	# currentOrders = json.loads(currentOrders)
	upTable = frappe.get_doc("Tables", table)

	upTable.update(
		{
			"current_orders": []
		}
	)
	upTable.save()
	upTable.update(
		{
			"current_orders": curr_order
		}
	)

	upTable.save()
	if sio.connected:
		sio.emit(f'{upTable.get("company")}_table_refresh')
	frappe.local.response['status'] = "OK"

"""
Get today's kitchen and bar orders for a given company and table.

Parameters:
- company (str): The name of the company.
- table (str): The name of the table.

Returns:
- dict: A dictionary containing the kitchen and bar orders for today.

Description:
This function retrieves the kitchen and bar orders for today for a given company and table. It first retrieves the current date using the 'datetime.now().date()' function. Then, it uses the 'frappe.get_list' function to retrieve the kitchen orders and bar orders with the specified company, created date, and table name.

For each kitchen order, it creates a dictionary with the keys 'kotId', 'created_time', 'remark', and 'items'. It retrieves the kitchen order document using the 'frappe.get_doc' function and populates the dictionary with the relevant information from the document. For each item in the kitchen order, it retrieves the food child document using the 'frappe.get_doc' function and retrieves the item name from the 'Item' document using the 'frappe.db.get_value' function. It then appends a dictionary with the keys 'item_code', 'item_name', and 'quantity' to the 'items' list in the kitchen order dictionary. Finally, it appends the kitchen order dictionary to the 'kotOrders' list.

The process is similar for bar orders. For each bar order, it creates a dictionary with the keys 'botId', 'created_time', 'remark', and 'items'. It retrieves the bar order document using the 'frappe.get_doc' function and populates the dictionary with the relevant information from the document. For each item in the bar order, it retrieves the bar child document using the 'frappe.get_doc' function and retrieves the item name from the 'Item' document using the 'frappe.db.get_value' function. It then appends a dictionary with the keys 'item_code', 'item_name', and 'quantity' to the 'items' list in the bar order dictionary. Finally, it appends the bar order dictionary to the 'botOrders' list.

Finally, it returns a dictionary with the keys 'kot' and 'bot' containing the kitchen and bar orders respectively.

Note:
- This function requires the 'frappe' module to be imported.
- The 'datetime.now().date()' function is used to retrieve the current date.
- The 'frappe.get_list' function is used to retrieve the kitchen and bar orders.
- The 'frappe.get_doc' function is used to retrieve the kitchen and bar order documents.
- The 'frappe.db.get_value' function is used to retrieve the item name from the 'Item' document.
- The 'datetime.strftime' function is used to format the creation time of the orders.
"""
@frappe.whitelist()
def getTodaysKotBot(company, table):
	print(datetime.now().date())
	kot = frappe.get_list(
		"Kitchen Orders", {"company": company, "created_date": datetime.now().date(), "table_name": table})
	bot = frappe.get_list(
		"Bar Orders", {"company": company, "created_date": datetime.now().date(), "table_name": table})

	kotOrders = []
	botOrders = []

	for k in kot:
		kDict = {"kotId": "", "created_time": "", "remark": "", "items": []}
		ko = frappe.get_doc("Kitchen Orders", k.name)
		kDict['kotId'] = ko.kot_id
		kDict['remark'] = ko.remark
		kDict["created_time"] = datetime.strftime(ko.creation, "%H:%M")
		for ki in ko.items:
			item = frappe.get_doc("Food Child", ki.name)
			itemName = frappe.db.get_value(
				"Item", item.item_code, "item_name")
			kDict['items'].append({
				"item_code": item.item_code,
				"item_name": itemName,
				"quantity": item.quantity

			})
		kotOrders.append(kDict)

	for b in bot:
		bDict = {"botId": "", "created_time": "", "items": [], }
		bo = frappe.get_doc("Bar Orders", b.name)
		bDict['botId'] = bo.bot_id
		bDict['remark'] = bo.remark
		bDict["created_time"] = datetime.strftime(bo.creation, "%H:%M")
		for bi in bo.items:
			item = frappe.get_doc("Bar Child", bi.name)
			itemName = frappe.db.get_value(
				"Item", item.item_code, "item_name")
			bDict['items'].append({
				"item_code": item.item_code,
				"item_name": itemName,
				"quantity": item.quantity

			})
		botOrders.append(bDict)

	frappe.local.response['data'] = {"kot": kotOrders, "bot": botOrders}

"""
Get printer details for the current user.

Returns:
- printerDetails (dict): A dictionary containing the printer details.

Description:
This function retrieves the printer details for the current user. It first gets the current user's email address using the 'frappe.session.user' attribute. Then, it retrieves the waiter profile document for the user using the 'frappe.get_doc' function with the "Waiter Profile" doctype and the user's email address as the filters.

Next, it retrieves the printer details document for the outlet specified in the waiter profile using the 'frappe.get_doc' function with the "Restaurant names" doctype and the outlet as the filters.

Finally, it returns the printer details as a dictionary.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.session.user' attribute is used to get the current user's email address.
- The 'frappe.get_doc' function is used to retrieve the waiter profile and printer details documents.
- The "Waiter Profile" and "Restaurant names" doctypes are used to filter the documents.
"""
@frappe.whitelist()
def getPrinterDetails():
	user = frappe.session.user
	waiterProfile = frappe.get_cached_doc("Waiter Profile", user)

	printerDetails = frappe.get_cached_doc("Restaurant names", waiterProfile.outlet)

	frappe.local.response['data'] = printerDetails


"""
Create an order for home delivery.

Parameters:
- orderItems (str): A JSON string representing the order items. Each item should have the following keys: 'item_code', 'parent', and 'quantity'.
- company (str): The name of the company.

Returns:
- str: A message indicating the status of the order creation.

Description:
This function creates an order for home delivery. It first retrieves the email of the current user from the session. Then, it gets the current date and time using the 'datetime.now().date()' function. The 'orderItems' parameter is parsed from a JSON string to a Python object using the 'json.loads' function.

Next, it creates a new document of type 'Home Delivery Orders' using the 'frappe.get_doc' function. The document is initialized with the email, company, and created date.

For each order item in the 'orderItems' list, it retrieves the rate and tax information from the 'Sub Category Items' document using the 'frappe.db.get_value' function. Then, it appends a new 'delivery_items' child document to the main document. The 'delivery_items' document is populated with the item code, quantity, rate, tax, and parent name.

After adding all the order items, the main document is inserted into the database using the 'doc.insert()' method. The document status is set to '1' (submitted) using the 'frappe.db.set_value' function. Finally, the changes are committed to the database using the 'frappe.db.commit()' function.

The function returns a message indicating the status of the order creation.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.session.user' attribute is used to get the email of the current user.
- The 'datetime.now().date()' function is used to get the current date.
- The 'json.loads' function is used to parse the 'orderItems' parameter from a JSON string to a Python object.
- The 'frappe.get_doc' function is used to create a new document of type 'Home Delivery Orders'.
- The 'frappe.db.get_value' function is used to retrieve the rate and tax information from the 'Sub Category Items' document.
- The 'doc.append' method is used to add new 'delivery_items' child documents to the main document.
- The 'doc.insert' method is used to insert the main document into the database.
- The 'frappe.db.set_value' function is used to set the document status to '1'.
- The 'frappe.db.commit' function is used to commit the changes to the database.
"""
@frappe.whitelist()
def createAnOrder(orderItems, company):
	email = frappe.session.user
	created_date = datetime.now().date()
	orderItems = json.loads(orderItems)

	doc = frappe.get_doc(
		{"doctype": "Home Delivery Orders", "email": email, "company": company, 'created_date': created_date})

	for o in orderItems:
		itemData = frappe.db.get_value(
			"Sub Category Items", {'item_code': o['item_code'], 'parent': o['parent']}, ['rate', 'tax'], as_dict=True)

		delivery_itm = doc.append('delivery_items', {})
		delivery_itm.item_code = o['item_code']
		delivery_itm.quantity = o['quantity']
		delivery_itm.rate = itemData['rate']
		delivery_itm.tax = itemData['tax']
		delivery_itm.parentname = o['parent']

	doc.insert()
	frappe.db.set_value("Home Delivery Orders",
						doc.name, 'docstatus', '1')

	notifications = frappe.new_doc("Sajha Notification")
	notifications.company = company
	notifications.notification = f"You have an order from {doc.username} with order number {doc.name}"
	notifications.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.local.response['data'] = "Order Created"

"""
Get the list of home delivery orders for the current user.

Returns:
	list: A list of dictionaries containing the order details.

Description:
	This function retrieves the home delivery orders for the current user. It first gets the email of the current user from the session. Then, it uses the 'frappe.get_list' function to get a list of home delivery orders filtered by the user's email.

	For each order, a dictionary is created with the following keys:
	- 'orderId': The ID of the order.
	- 'orderName': The name of the order.
	- 'image': The image of the first item in the order.
	- 'date': The creation date of the order.
	- 'numberOfItems': The number of items in the order.
	- 'total': The total cost of the order.
	- 'status': The status of the order.

	The dictionary is then appended to the 'orders' list.

	Finally, the function returns the 'orders' list containing the order details.

Note:
	- This function requires the 'frappe' module to be imported.
	- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
	- The 'frappe.session.user' attribute is used to get the email of the current user.
	- The 'frappe.get_list' function is used to retrieve a list of home delivery orders filtered by the user's email.
	- The 'frappe.get_doc' function is used to retrieve the order document and the item document.
"""
@frappe.whitelist()
def getMyOrder():
	email = frappe.session.user
	myOrders = frappe.get_list(
		"Home Delivery Orders", filters={"email": email})
	orders = []
	title = ""

	for order in myOrders:
		oi = {"orderId": "", "orderName": "",
			  "image": "", "date": "", "numberOfItems": 0, "total": 0, "status": ""}
		o = frappe.get_doc("Home Delivery Orders", order.name)
		oi['orderId'] = o.name
		oi["date"] = o.creation
		item = frappe.get_doc("Item", o.delivery_items[0].item_code)
		oi['numberOfItems'] = len(o.delivery_items)
		oi['image'] = item.image
		oi['status'] = o.status
		for ord in o.delivery_items:

			oi['total'] += round((ord.rate + ord.tax) * ord.quantity)

			title = str(f'{title} ,' + ord.hidden_name).strip()
		oi['orderName'] = title
		orders.append(oi)

	return orders


"""
Get order item details for a given order ID.

Parameters:
- orderId (str): The ID of the order.

Returns:
- dict: A dictionary containing the order item details.

Description:
This function retrieves the order item details for a given order ID. It first initializes an empty string variable 'title' and a dictionary variable 'oi' with keys 'orderId', 'orderName', 'image', 'date', 'orderedItems', and 'status'.

Next, it retrieves the 'Home Delivery Orders' document with the given order ID using the 'frappe.get_doc' function. The 'orderId' key in the 'oi' dictionary is set to the name of the order document, and the 'date' key is set to the creation date of the order document.

Then, it retrieves the 'Item' document for the first delivery item in the order using the 'frappe.get_doc' function. The 'image' key in the 'oi' dictionary is set to the image of the item document.

Next, it iterates over each delivery item in the order and appends a dictionary to the 'orderedItems' list in the 'oi' dictionary. Each dictionary contains the keys 'itemCode', 'item_name', 'quantity', 'itemPrice', and 'parent', which correspond to the item code, hidden name, quantity, item price (rate + tax), and parent name of the delivery item, respectively.

After iterating over all delivery items, the 'status' key in the 'oi' dictionary is set to the status of the order document.

Finally, the 'orderName' key in the 'oi' dictionary is set to the value of the 'title' variable, which contains the concatenated hidden names of all delivery items. The 'oi' dictionary is then returned.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.get_doc' function is used to retrieve the 'Home Delivery Orders' document and the 'Item' document.
- The 'ignore_permissions' parameter is set to True to bypass permission checks when retrieving the documents.
- The 'oi' dictionary is used to store the order item details.
- The 'oi['orderId']', 'oi['orderName']', 'oi['image']', 'oi['date']', 'oi['orderedItems']', and 'oi['status']' keys are used to store the corresponding values.
- The 'title' variable is used to concatenate the hidden names of all delivery items.
- The 'oi' dictionary is returned as the output of the function.
"""
@frappe.whitelist()
def getOrderItemDetail(orderId):

	title = ""
	oi = {"orderId": "", "orderName": "",
		  "image": "", "date": "", "orderedItems": [], 'status': ""}
	o = frappe.get_doc("Home Delivery Orders",
					   f"{orderId}", ignore_permissions=True)
	oi['orderId'] = o.name
	oi["date"] = o.creation
	doc = frappe.get_doc(
		"Item", o.delivery_items[0].item_code, ignore_permissions=True)
	oi['image'] = doc.image
	for ord in o.delivery_items:
		title = str(f'{title} ,' + ord.hidden_name).strip()
		oi['orderedItems'].append({
			"itemCode": ord.item_code,
			"item_name": ord.hidden_name,
			"quantity": ord.quantity,
			"itemPrice": round(ord.rate + ord.tax),
			"parent": ord.parentname
		})
	oi['status'] = o.status
	oi['orderName'] = title
	return oi


"""
Retrieve home screen data for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- dict: A dictionary containing the home screen data.

Description:
This function retrieves the home screen data for a given company. It first retrieves a list of room types, hall types, and special sub category items using the 'frappe.get_list' function with filters on the company name and other criteria.

Next, it initializes an empty dictionary called 'homeData' to store the home screen data.

Then, for each room type in the list of room types, it retrieves the room type document using the 'frappe.get_doc' function. It also retrieves the item price for the room type using the 'frappe.db.get_value' function. The room type details, including the room type code, room type name, available rooms, number of beds, maximum guests per room, total rooms, price per night, and image, are added to the 'ourRooms' list in the 'homeData' dictionary.

Similarly, for each hall type in the list of hall types, it retrieves the hall type document using the 'frappe.get_doc' function. The hall type details, including the hall name, capacity, image, area, wifi availability, shape, and description, are added to the 'halls' list in the 'homeData' dictionary.

Finally, for each special sub category item in the list of special sub category items, it retrieves the sub category item document using the 'frappe.get_doc' function. It also retrieves the item details using the 'frappe.db.get_value' function. The sub category item details, including the item code, item name, description, image, tax, rate, and parent, are added to the 'hotelSpecial' list in the 'homeData' dictionary.

The 'homeData' dictionary containing the home screen data is then returned.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of room types, hall types, and special sub category items.
- The 'frappe.get_doc' function is used to retrieve room type, hall type, and sub category item documents.
- The 'frappe.db.get_value' function is used to retrieve item prices and item details.
- The 'homeData' dictionary is used to store the home screen data.
- The 'append' method is used to add room type, hall type, and sub category item details to the respective lists in the 'homeData' dictionary.
"""
@frappe.whitelist(allow_guest=True)
def homeScreenData(company):
	roomType = frappe.get_list(
		"Room Type HMS", {"company": company}, limit=5,  ignore_permissions=True)
	halls = frappe.get_list(
		"Hall Type", {"company": company}, limit=5, ignore_permissions=True)
	special = frappe.get_list("Sub Category Items", filters={"hotel_special": 1, "todisplay": 1, "company": company}, limit=5, ignore_permissions=True)

	homeData = {
		'ourRooms': [],
		'hotelSpecial': [],
		'halls': []
	}

	for room in roomType:
		rt = frappe.get_doc("Room Type HMS", room.name)

		item = frappe.db.get_value("Item Price", {'item_code': rt.item, 'selling': 1}, [
			'price_list_rate'], as_dict=True)
		homeData['ourRooms'].append({
			'name':rt.name,
			'roomTypeCode': rt.room_type_code,
			'roomTypeName': rt.room_type,
			'availableRoom': rt.available_room,
			'beds': rt.beds,
			'maxGuestPerRoom': rt.max_guest_per_room,
			'totalRoom': rt.total_room,
			'pricePerNight': item.price_list_rate,
			'image': rt.image,
		})

	for hall in halls:
		hr = frappe.get_doc("Hall Type", hall.name, ignore_permissions=True)

		homeData['halls'].append({
			"hallName": hr.hall_name,
			"capacity": hr.capacity,
			"image": hr.image,
			"area": hr.area,
			"wifi": hr.wifi,
			"shape": hr.shape,
			"description": hr.description,
		})

	for spe in special:
		itemName = frappe.get_doc(
			"Sub Category Items", spe.name)

		item = frappe.db.get_value("Item", {'item_code': itemName.item_code}, [
			'item_code', 'item_name', "description", "image",], as_dict=True)

		homeData['hotelSpecial'].append(
			{"item": {"item_code": item['item_code'], "item_name": item['item_name'], "description": itemName.description, "image": item['image']}, 'tax': itemName.tax, 'rate': itemName.rate, "parent": itemName.parent})

	frappe.local.response['data'] = homeData

"""
Get all special items for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the special item data.

Description:
This function retrieves all special items for a given company. It first retrieves a list of special subcategory items using the 'frappe.get_list' function with filters on the 'hotel_special', 'todisplay', and 'company' fields. For each special subcategory item, it retrieves the corresponding item document using the 'frappe.get_doc' function with a filter on the item name.

Next, it retrieves specific fields from the item document using the 'frappe.db.get_value' function. The fields include the item code, item name, description, and image.

Then, it appends a dictionary to the 'specialItem' list for each special subcategory item. The dictionary contains the item data, description, tax, rate, and parent subcategory item.

Finally, it returns the 'specialItem' list containing the special item data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve a list of special subcategory items.
- The 'frappe.get_doc' function is used to retrieve the item document for each special subcategory item.
- The 'frappe.db.get_value' function is used to retrieve specific fields from the item document.
- The 'specialItem' list is used to store the special item data.
"""
@frappe.whitelist(allow_guest=True)
def getAllSpecial(company):
	special = frappe.get_list("Sub Category Items",
							  filters={"hotel_special": 1, "todisplay": 1, "company": company}, ignore_permissions=True)
	specialItem = []
	for spe in special:
		itemName = frappe.get_doc(
			"Sub Category Items", spe.name)
		item = frappe.db.get_value("Item", {'item_code': itemName.item_code}, [
			'item_code', 'item_name', "description", "image",], as_dict=True)

		specialItem.append(
			{"item": item, 'description': itemName.description, 'tax': itemName.tax, 'rate': itemName.rate, "parent": itemName.parent})
	frappe.local.response['data'] = specialItem

"""
Get a list of customers.

Returns:
- list: A list of dictionaries containing customer details.

Description:
This function retrieves a list of customers from the 'Customer' table in the database. It uses the 'frappe.db.get_list' function to fetch the customer records with the specified fields: 'name', 'customer_name', and 'mobile_number'. The customer details are returned as a list of dictionaries, where each dictionary represents a customer and contains the 'name', 'customer_name', and 'mobile_number' fields.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_list' function is used to retrieve the customer records.
- The 'fields' parameter is used to specify the fields to be fetched from the customer records.
"""
@frappe.whitelist()
def get_customers(searchTerm):
	return frappe.db.get_list(doctype='Customer', or_filters={"name": ['like', f"%{searchTerm}%"], "mobile_no":['like', f"%{searchTerm}%"]} ,  fields=['name', 'customer_name', 'mobile_no', 'loyalty_points'])



@frappe.whitelist()
def get_credit(customer):
	data = get_dashboard_info("Customer", customer)
	return data


"""
Get customer fields.

Returns:
- dict: A dictionary containing the territories, customer groups, and companies.

Description:
This function retrieves the territories, customer groups, and companies from the database. It first retrieves a list of territories using the 'frappe.db.get_list' function with no filters. Then, it retrieves a list of customer groups and companies using the same function with the respective doctype names.

Finally, it returns a dictionary containing the territories, customer groups, and companies.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_list' function is used to retrieve the territories, customer groups, and companies.
- The 'territories' key in the returned dictionary contains the list of territories.
- The 'customer_group' key in the returned dictionary contains the list of customer groups.
- The 'companies' key in the returned dictionary contains the list of companies.
"""
@frappe.whitelist()
def get_customer_fields():
	territories = frappe.db.get_list("Territory")
	customer_group = frappe.db.get_list('Customer Group')
	companies = frappe.db.get_list('Company')

	return {'territories': territories, 'customer_group': customer_group, 'companies': companies}


"""
Get customer fields.

Returns:
- dict: A dictionary containing the territories, customer groups, and companies.

Description:
This function retrieves the territories, customer groups, and companies from the database. It first retrieves a list of territories using the 'frappe.db.get_list' function with no filters. Then, it retrieves a list of customer groups and companies using the same function with the respective doctype names.

Finally, it returns a dictionary containing the territories, customer groups, and companies.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_list' function is used to retrieve the territories, customer groups, and companies.
- The 'territories' key in the returned dictionary contains the list of territories.
- The 'customer_group' key in the returned dictionary contains the list of customer groups.
- The 'companies' key in the returned dictionary contains the list of companies.
"""
@frappe.whitelist()
def insert_customer(address_line1, customer_territory, city, country, customer_group, customer_name, type, mobile_no, address_line2="", state="", email="", pan="", zip=""):

		c_doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_group": customer_group,
			"territory": customer_territory,
			"customer_type": type,
			"mobile_no": mobile_no,
			"pan": pan
		})
		c_doc.insert()

		contact = frappe.db.get_value(
			"Contact", f"{c_doc.name}-{c_doc.name}", "name")
		if contact != None:
			contactData = frappe.get_doc(
				"Contact", f"{c_doc.name}-{c_doc.name}")


			contactData.email_id = email if contactData.email_id == None else contactData.email_id
			contactData.address1 = address_line1 if (contactData.address1 == None) or (
				contactData.address1 == "placeholder") else contactData.address1
			contactData.address2 = address_line2 if contactData.address2 == None else contactData.address2
			contactData.city = city if contactData.city == None else contactData.city
			contactData.state = state if contactData.state == None else contactData.state
			contactData.country = country if (contactData.country == None) or (
				contactData.country == "placeholder") else contactData.country
			contactData.postal_code = zip if contactData.postal_code == None else contactData.postal_code
			contactData.save()
		else:
			doc = frappe.new_doc("Contact")
			doc.first_name = c_doc.name
			doc.email_id = email
			doc.address1 = address_line1
			doc.address2 = address_line2
			doc.city = city
			doc.state = state
			doc.country = country
			doc.postal_code = zip

			if (mobile_no != ""):
				contact_item = doc.append("phone_nos", {})
				contact_item.phone = mobile_no
				contact_item.is_primary_mobile_no = 1
				contact_item.is_primary_phone = 1

			customer_ref = doc.append("links", {})
			customer_ref.link_doctype = "Customer"
			customer_ref.link_name = customer_name
			doc.save()

		return True




"""
Cancel an order.

Parameters:
- orderId (str): The ID of the order to be cancelled.

Returns:
- str: The status code indicating the result of the cancellation.

Description:
This function cancels an order by updating the document status and status fields in the 'Home Delivery Orders' collection. It first retrieves the user's email address from the session. Then, it retrieves the order document using the provided orderId and ignores the permissions.

If the document exists and the email address matches the document's email field, the function checks if the status of the order is "Order Received". If it is, the function updates the document's docstatus field to '2' (cancelled) and the status field to 'Order Cancelled'. The changes are then committed to the database.

Finally, the function returns a status code indicating the result of the cancellation. If the cancellation is successful, the status code is "SCC200". If the document does not exist, the status code is "ERR404". If the email address does not match the document's email field, the status code is "ERR401". If the status of the order is not "Order Received", the status code is "ERR403".

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.session.user' attribute is used to get the user's email address.
- The 'frappe.get_doc' function is used to retrieve the order document.
- The 'ignore_permissions' parameter is set to True to bypass permission checks.
- The 'frappe.db.set_value' function is used to update the document fields.
- The 'frappe.db.commit' function is used to commit the changes to the database.
"""
@frappe.whitelist()
def cancelOrder(orderId):
	email = frappe.session.user

	doc = frappe.get_doc("Home Delivery Orders", orderId,
							ignore_permissions=True)

	if doc != None:
		if doc.email == email:
			if (doc.status == "Order Received"):
				frappe.db.set_value("Home Delivery Orders",
									doc.name, 'docstatus', '2')
				frappe.db.set_value("Home Delivery Orders",
									doc.name, 'status', 'Order Cancelled')
				frappe.db.commit()

				frappe.local.response['code'] = "SCC200"
			else:
				frappe.local.response['code'] = "ERR403"

		else:
			frappe.local.response['code'] = "ERR401"
	else:
		frappe.local.response['code'] = "ERR404"

"""
Reorder the items in an order.

Parameters:
- orderedItem (str): A JSON string representing the ordered items.

Returns:
- list: A list of dictionaries containing the reordered item data.

Description:
This function takes a JSON string representing the ordered items and reorders them. It first converts the JSON string into a Python list of dictionaries using the 'json.loads' function. Then, for each item in the ordered items, it retrieves the rate and tax information from the 'Sub Category Items' document using the 'frappe.db.get_value' function. It creates a new dictionary with the item code, item name, quantity, rate, tax, and parent information, and appends it to the 'newItemRate' list.

Finally, it returns the 'newItemRate' list containing the reordered item data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'json.loads' function is used to convert the JSON string into a Python list of dictionaries.
- The 'frappe.db.get_value' function is used to retrieve the rate and tax information from the 'Sub Category Items' document.
- The 'newItemRate' list is used to store the reordered item data.
"""
@frappe.whitelist(allow_guest=True)
def reorderOrder(orderedItem):
	orderedItem = json.loads(orderedItem)
	newItemRate = []
	for o in orderedItem:
		itemData = frappe.db.get_value(
			"Sub Category Items", {'item_code': o['itemCode'], 'parent': o['parent'], 'todisplay': 1}, ['rate', 'tax'], as_dict=True)
		newItemRate.append({
			'itemCode': o['itemCode'],
			'item_name': o['item_name'],
			'quantity': o['quantity'],
			'rate': itemData['rate'],
			'tax': itemData['tax'],
			'parent': o['parent'],
		})
	frappe.local.response['data'] = newItemRate


"""
Get outlet data for the current user.

Returns:
- list: A list of dictionaries containing the outlet data.

Description:
This function retrieves the outlet data for the current user. It first retrieves the current user's email address using the 'frappe.session.user' attribute. Then, it retrieves the user document using the 'frappe.get_doc' function. Next, it retrieves a list of restaurant names using the 'frappe.get_list' function with a filter on the user's company. The 'ignore_permissions' parameter is set to True to bypass permission checks.

Finally, it returns the list of restaurant names as the outlet data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow the function to be called from the client side.
- The 'frappe.session.user' attribute is used to get the current user's email address.
- The 'frappe.get_doc' function is used to retrieve the user document.
- The 'frappe.get_list' function is used to retrieve a list of restaurant names.
- The 'filter' parameter is used to filter the restaurant names by the user's company.
- The 'ignore_permissions' parameter is set to True to bypass permission checks.
"""
@frappe.whitelist()
def getOutlet():
	user = frappe.session.user
	userCompany = frappe.get_doc("User", user)
	doc = frappe.get_all("Restaurant names", {
		"company": userCompany.get("company")},['name'], ignore_permissions=True)
	frappe.local.response['data'] = doc


"""
Get the naming series options for the Sales Invoice doctype.

Returns:
- list: A list of strings representing the available naming series options.

Description:
This function retrieves the naming series options for the Sales Invoice doctype. It uses the 'frappe.get_meta' function to get the metadata for the Sales Invoice doctype, and then retrieves the 'naming_series' field from the metadata. The function returns a list of strings representing the available naming series options.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_meta' function is used to retrieve the metadata for the Sales Invoice doctype.
- The 'get_field' method is used to retrieve the 'naming_series' field from the metadata.
- The 'options' attribute is used to get the available naming series options.
"""
@frappe.whitelist(allow_guest=True)
def get_naming_series():
	return frappe.get_meta("Sales Invoice").get_field("naming_series").options

"""
Get the mode of payment options for the current user's company.

Returns:
- list: A list of dictionaries containing the mode of payment options.

Description:
This function retrieves the mode of payment options for the current user's company. It first retrieves a list of mode of payment documents that are enabled using the 'frappe.db.get_list' function with a filter on the 'enabled' field. For each mode of payment document, it retrieves the mode of payment document using the 'frappe.get_doc' function.

Next, it checks if the mode of payment document has an account that belongs to the current user's company. If it does, it appends a new dictionary to the 'modeOfPayment' list with the mode of payment name and type.

Finally, it returns the 'modeOfPayment' list containing the mode of payment options.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'frappe.db.get_list' function is used to retrieve a list of mode of payment documents.
- The 'frappe.get_doc' function is used to retrieve mode of payment documents.
- The 'filter' parameter is used to filter the mode of payment documents by the 'enabled' field.
- The 'modeOfPayment' list is used to store the mode of payment options.
- The 'frappe.session.user' attribute is used to get the current user's email address.
- The 'frappe.get_doc' function is used to retrieve the user document.
- The 'user.get' method is used to get the company name of the user.
- The 'mop.accounts' attribute is used to access the accounts of the mode of payment document.
- The 'append' method is used to add new dictionaries to the 'modeOfPayment' list.
"""
@frappe.whitelist(allow_guest=True)
def get_mode_of_payment():
	doc = frappe.db.get_list("Mode of Payment", {"enabled": 1}, [
		'name', 'type'], ignore_permissions=True)
	modeOfPayment = []
	user = frappe.session.user
	userCompany = frappe.get_doc("User", user).get("company")
	for pay in doc:
		mop = frappe.get_doc("Mode of Payment", pay.name)
		for account in mop.accounts:
			if account.company == userCompany:
				modeOfPayment.append({
					"name": pay.name,
					"type": pay.type
				})

	frappe.local.response['data'] = modeOfPayment

"""
Shift the orders and total charges from one table to another.

Parameters:
- shift_from (str): The name of the table from which the orders and total charges are shifted.
- shift_to (str): The name of the table to which the orders and total charges are shifted.

Returns:
- str: "OK" if the shift is successful, "ERROR" if an error occurs.

Description:
This function shifts the current orders, total orders, and total charges from one table to another. It first retrieves the 'from_shift' and 'to_shift' table documents using the 'frappe.get_doc' function. Then, it retrieves the current orders, total orders, and total charges from the 'from_shift' table.

Next, it combines the current orders from both tables, ensuring that there are no duplicate items. If an item already exists in the 'to_shift' table, the quantity is updated accordingly. The combined current orders are then assigned to the 'current_orders' field of the 'to_shift' table.

Similarly, it combines the total orders from both tables, ensuring that there are no duplicate items. If an item already exists in the 'to_shift' table, the quantity is updated accordingly. The combined total orders are then assigned to the 'orders' field of the 'to_shift' table.

If there are any 'kot_bot' entries in the 'from_shift' table, they are moved to the 'to_shift' table.

Next, it calculates the total charges for the 'from_shift' table based on the quantity and rate of each item. If there are no orders in the 'from_shift' table, the total charges are set to 0. The total charges are then assigned to the 'total_charges' field of the 'from_shift' table.

Similarly, it calculates the total charges for the 'to_shift' table based on the quantity and rate of each item. If there are no orders in the 'to_shift' table, the total charges are set to 0. The total charges are then assigned to the 'total_charges' field of the 'to_shift' table.

Finally, it saves the changes to both table documents and returns "OK" if the shift is successful. If an error occurs, it returns "ERROR".

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table documents.
- The 'from_shift.current_orders', 'from_shift.orders', and 'from_shift.kot_bot' attributes are used to retrieve the current orders, total orders, and kot_bot entries from the 'from_shift' table.
- The 'to_shift.current_orders', 'to_shift.orders', and 'to_shift.kot_bot' attributes are used to assign the combined current orders, combined total orders, and kot_bot entries to the 'to_shift' table.
- The 'frappe.get_doc' function is used to retrieve the item category document for calculating the total charges.
- The 'table.total_charges' attribute is used to assign the total charges to the table documents.
- The 'table.db_update' method is used to save the changes to the table documents.
- The 'from_shift.save' and 'to_shift.save' methods are used to save the changes to the table documents.
"""
@frappe.whitelist()
def shiftTable(shift_from, shift_to):
	try:
		from_shift = frappe.get_doc(
			"Tables", shift_from, ignore_permissions=True)
		to_shift = frappe.get_doc("Tables", shift_to, ignore_permissions=True)
		if from_shift.get("kot_bot"):
			doc = frappe.db.get_value("KOT_BOT",{'ticket_name':from_shift.kot_bot[0].ticket_name, 'parenttype': "Sales Invoice"}, "is_split")
			if doc is not None:
				return {"code": "ALREADY_EXISTS", 'invoice': doc}

		current_orders_from = from_shift.current_orders
		total_orders_from = from_shift.orders
		kot_bot_from = from_shift.kot_bot

		current_orders_to = to_shift.current_orders
		total_orders_to = to_shift.orders

		combined_current_order = []
		combined_total_orders = []

		if (len(current_orders_from) > 0 or len(current_orders_to) > 0):
			for o in current_orders_from:
				combined_current_order.append(
					{'item_code': o.item_code, 'quantity': o.quantity, 'parent_name': o.parent_name})

			for order in current_orders_to:
				def item_check(v):
					return v['item_code'] == order.item_code
				item = next(filter(item_check, combined_current_order), None)

				if item is None:
					combined_current_order.append(
						{'item_code': order.item_code, 'quantity': order.quantity, 'parent_name': order.parent_name})
				else:
					index = next(i for i, x in enumerate(
						combined_current_order) if x['item_code'] == order.item_code)

					combined_current_order[index]['quantity'] = combined_current_order[index]['quantity'] + int(
						order.quantity)

			to_shift.current_orders = []


			for ord in combined_current_order:
				current_orders_child = to_shift.append('current_orders', {})
				current_orders_child.item_code = ord['item_code']
				current_orders_child.quantity = ord['quantity']
				current_orders_child.parent_name = ord['parent_name']

			from_shift.current_orders = []

		if (len(total_orders_from) > 0 or len(total_orders_to) > 0):
			for o in total_orders_from:
				combined_total_orders.append(
					{'item': o.item, 'quantity': o.quantity})

			for order in total_orders_to:
				def item_check(v):
					return v['item'] == order.item
				item = next(filter(item_check, combined_total_orders), None)

				if item is None:
					combined_total_orders.append(
						{'item': order.item, 'quantity': order.quantity})
				else:
					index = next(i for i, x in enumerate(
						combined_total_orders) if x['item'] == order.item)

					combined_total_orders[index]['quantity'] = combined_total_orders[index]['quantity'] + int(
						order.quantity)

			to_shift.orders = []

			for ord in combined_total_orders:
				orders_child = to_shift.append('orders', {})
				orders_child.item = ord['item']
				orders_child.quantity = ord['quantity']

			from_shift.orders = []

		if (len(kot_bot_from) > 0 or len(kot_bot_from) > 0):
			for ord in kot_bot_from:
				orders_child = to_shift.append('kot_bot', {})
				orders_child.ticket_number = ord.ticket_number
				orders_child.ticket_name = ord.ticket_name

			from_shift.kot_bot = []

		totalCharges = 0.00
		if len(from_shift.get("orders")) > 0:
			for o in from_shift.get("orders"):
				itemCategory = frappe.get_doc(
					"Sub Category Items", {"item_code": o.item})
				totalCharges = totalCharges + \
					(o.quantity * (itemCategory.rate))
			table = frappe.get_doc("Tables", from_shift.get("name"))
			table.total_charges = totalCharges
			table.db_update()

		else:
			table = frappe.get_doc("Tables", from_shift.get("name"))
			table.total_charges = 0.00
			table.db_update()

		totalCharges = 0.00
		if len(to_shift.get("orders")) > 0:
			for o in to_shift.get("orders"):
				itemCategory = frappe.get_doc(
					"Sub Category Items", {"item_code": o.item})
				totalCharges = totalCharges + \
					(o.quantity * (itemCategory.rate))
			table = frappe.get_doc("Tables", to_shift.get("name"))
			table.total_charges = totalCharges
			table.db_update()

		else:
			table = frappe.get_doc("Tables", to_shift.get("name"))
			table.total_charges = 0.00
			table.db_update()

		from_shift.save()
		to_shift.save()

		for kot_bot in to_shift.kot_bot:
			if "KOT" in kot_bot.ticket_number:
				frappe.db.set_value("Kitchen Orders", kot_bot.ticket_name, "table_name", to_shift.name)
			else:
				frappe.db.set_value("Bar Orders", kot_bot.ticket_name, "table_name", to_shift.name)


		return "OK"
	except:
		return "ERROR"

"""
Get outlet tables for a given outlet.

Parameters:
- outlet (str): The name of the outlet.

Returns:
- list: A list of dictionaries containing the outlet table data.

Description:
This function retrieves the outlet tables for a given outlet. It uses the 'frappe.get_list' function to retrieve a list of tables with the specified outlet name. The table data includes the table name and the enabled status. The function ignores permissions when retrieving the table data.

The function returns a list of dictionaries, where each dictionary represents a table. Each table dictionary contains the table name and the enabled status.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_list' function is used to retrieve the table data.
- The 'ignore_permissions' parameter is set to True to ignore permissions when retrieving the table data.
"""
@frappe.whitelist(allow_guest=True)
def getOutletTables(outlet):
	doc = frappe.get_list("Tables", {"restaurant_names": outlet}, [
		'name', 'enabled'], ignore_permissions=True)

	return doc

"""
Set the status of a table.

Parameters:
- table (str): The name of the table.
- status (bool): The status to set for the table.

Returns:
- str: The status of the table after setting.

Description:
This function sets the status of a table. It first retrieves the table document using the 'frappe.get_doc' function. Then, it updates the 'enabled' attribute of the table document with the provided status. Finally, it saves the changes to the table document using the 'doc.db_update' method and returns the updated status of the table.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table document.
- The 'doc.enabled' attribute is used to update the status of the table.
- The 'doc.db_update' method is used to save the changes to the table document.
"""
@frappe.whitelist()
def setTableStatus(table, status):
	try:
		doc = frappe.get_doc("Tables", table)
		doc.enabled = status
		doc.db_update()
		return "OK"
	except:
		return "ERR"

"""
Merge tables in the restaurant.

Parameters:
- data (str): A JSON string containing the data required for merging tables. It should have the following keys:
	- 'parentTable' (str): The name of the parent table.
	- 'mergeTablelist' (list): A list of table names to be merged with the parent table.

Returns:
- str: A string indicating the status of the merge operation. Possible values are:
	- 'OK': The merge operation was successful.
	- 'TNC': There was an error while merging the tables.
	- 'ERR': There was an error while processing the input data.

Description:
This function merges tables in a restaurant. It takes a JSON string as input, which contains the name of the parent table and a list of table names to be merged with the parent table. The function retrieves the parent table and the tables to be merged using the 'frappe.get_doc' function. It then combines the orders from the parent table and the merged tables, and updates the orders in the parent table. Similarly, it combines the 'kot_bot' entries from the merged tables and updates the 'kot_bot' entries in the parent table.

Next, the function calculates the total charges for the parent table based on the combined orders. If there are no orders, the total charges are set to 0.00. The function updates the 'total_charges' field in the parent table using the 'db_update' method.

Similarly, the function calculates the total charges for each merged table based on its orders. If there are no orders, the total charges are set to 0.00. The function updates the 'total_charges' field in each merged table using the 'db_update' method.

The function then updates the 'merged_tables' field in the parent table to include the names of the merged tables. If the 'merged_tables' field is already set, the names of the merged tables are appended to the existing value.

Finally, the function saves the changes to the parent table and each merged table using the 'save' method. If any error occurs during the merge operation, the function returns the corresponding status string.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the parent table and the merged tables.
- The 'parent_table.orders' attribute is used to access the orders in the parent table.
- The 'parent_table.append' method is used to add new orders to the parent table.
- The 'parent_table.kot_bot' attribute is used to access the 'kot_bot' entries in the parent table.
- The 'parent_table.save' method is used to save the changes to the parent table.
- The 'table.orders' attribute is used to access the orders in each merged table.
- The 'table.kot_bot' attribute is used to access the 'kot_bot' entries in each merged table.
- The 'table.total_charges' attribute is used to update the total charges in each merged table.
- The 'table.db_update' method is used to save the changes to each merged table.
- The 'parent_table.merged_tables' attribute is used to update the 'merged_tables' field in the parent table.
"""
@frappe.whitelist()
def mergeTables(data):
	try:
		data = json.loads(data)
		parent_table = data['parentTable']
		merge_table_list = data['mergeTablelist']

		for table in merge_table_list:
			try:
				to_shift = frappe.get_doc(
					"Tables", parent_table, ignore_permissions=True)

				total_orders_to = to_shift.orders

				combined_total_orders = []

				for o in total_orders_to:
					combined_total_orders.append(
						{'item': o.item, 'quantity': o.quantity})
				from_shift = frappe.get_doc(
					"Tables", table, ignore_permissions=True)
				total_orders_from = from_shift.orders
				kot_bot_from = from_shift.kot_bot

				if (len(total_orders_from) > 0 or len(total_orders_to) > 0):

					for order in total_orders_from:
						def item_check(v):
							return v['item'] == order.item
						item = next(
							filter(item_check, combined_total_orders), None)

						if item is None:
							combined_total_orders.append(
								{'item': order.item, 'quantity': order.quantity})
						else:
							index = next(i for i, x in enumerate(
								combined_total_orders) if x['item'] == order.item)

							combined_total_orders[index]['quantity'] = combined_total_orders[index]['quantity'] + int(
								order.quantity)

					to_shift.orders = []
					for ord in combined_total_orders:
						orders_child = to_shift.append('orders', {})
						orders_child.item = ord['item']
						orders_child.quantity = ord['quantity']

					from_shift.orders = []

				if (len(kot_bot_from) > 0 or len(kot_bot_from) > 0):
					for ord in kot_bot_from:
						orders_child = to_shift.append('kot_bot', {})
						orders_child.ticket_number = ord.ticket_number
						orders_child.ticket_name = ord.ticket_name

					from_shift.kot_bot = []
				totalCharges = 0.00
				if len(from_shift.get("orders")) > 0:
					for o in from_shift.get("orders"):
						itemCategory = frappe.get_doc(
							"Sub Category Items", {"item_code": o.item})
						totalCharges = totalCharges + \
							(o.quantity * (itemCategory.rate))
					tableData = frappe.get_doc(
						"Tables", from_shift.get("name"))
					tableData.total_charges = totalCharges
					tableData.db_update()
				else:
					tableData = frappe.get_doc(
						"Tables", from_shift.get("name"))
					tableData.total_charges = 0.00
					tableData.db_update()

				totalCharges = 0.00
				if len(to_shift.get("orders")) > 0:
					for o in to_shift.get("orders"):
						itemCategory = frappe.get_doc(
							"Sub Category Items", {"item_code": o.item})
						totalCharges = totalCharges + \
							(o.quantity * (itemCategory.rate))
					tableData = frappe.get_doc("Tables", to_shift.get("name"))
					tableData.total_charges = totalCharges
					tableData.db_update()
				else:
					tableData = frappe.get_doc("Tables", to_shift.get("name"))
					tableData.total_charges = 0.00
					tableData.db_update()
				if to_shift.merged_tables == None:
					to_shift.merged_tables = table
				else:
					to_shift.merged_tables = f"{to_shift.merged_tables}, {table}"
				from_shift.save()
				to_shift.save()
				for kot_bot in to_shift.kot_bot:
					if "KOT" in kot_bot.ticket_number:
						frappe.db.set_value("Kitchen Orders", kot_bot.ticket_name, "table_name", to_shift.name)
					else:
						frappe.db.set_value("Bar Orders", kot_bot.ticket_name, "table_name", to_shift.name)
			except:
				return "TNC"
		return "OK"
	except:

		return "ERR"

"""
Get item categories for a given company.

Parameters:
- company (str): The name of the company.

Returns:
- list: A list of dictionaries containing the item category data.

Description:
This function retrieves the item categories for a given company. It uses the 'frappe.db.get_list' function to retrieve a list of item categories with a filter on the company name. The 'name' field is specified in the 'fields' parameter to only retrieve the name of each item category. The function then returns the list of item categories.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_list' function is used to retrieve a list of item categories.
- The 'filter' parameter is used to filter the item categories by the company name.
- The 'fields' parameter is used to specify the 'name' field to be retrieved.
"""
@frappe.whitelist(allow_guest=True)
def get_item_category(company):
	doc = frappe.db.get_list(doctype="Item Category", filters={
		'company': company}, fields=['name'])

	return doc

"""
Search items based on a keyword and company.

Parameters:
- keyword (str): The keyword to search for in the item category names.
- company (str): The name of the company to filter the search.

Returns:
- list: A list of dictionaries containing the item category data.

Description:
This function searches for item categories based on a keyword and company. It uses the 'frappe.db.get_list' function to retrieve a list of item categories that match the given keyword and company. For each item category, it retrieves the item category document using the 'frappe.get_doc' function. It then appends a dictionary to the 'itemlist' list with the item category details, including the company, description, doctype, image, item category name, items, name, and todisplay.

Finally, it returns the 'itemlist' list containing the item category data.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_list' function is used to retrieve a list of item categories.
- The 'frappe.get_doc' function is used to retrieve the item category document.
- The 'itemlist' list is used to store the item category data.
- The 'append' method is used to add new dictionaries to the 'itemlist' list.
"""
@frappe.whitelist(allow_guest=True)
def search_items(keyword, company):
	item_category = frappe.db.get_list(doctype="Item Category", filters={
		"company": ['=', company], "name": ["like", f"%{keyword}%"]})
	itemlist = []

	for item in item_category:
		doc = frappe.get_doc("Item Category", item.name)
		itemlist.append({
			'company': doc.company,
			'description': doc.description,
			'doctype': doc.doctype,
			'image': doc.image,
			'item_category_name': doc.name,
			'items': doc.items,
			'name': doc.name,
			'todisplay': doc.todisplay
		})

	return itemlist

"""
Check if Tuna HMS is enabled.

Returns:
- bool: True if Tuna HMS is enabled, False otherwise.

Description:
This function checks if Tuna HMS (Hospital Management System) is enabled. It retrieves the value of the 'tuna_enable' field from the 'Sajha Menu Settings' document using the 'frappe.db.get_single_value' function. If the value is truthy, it returns True. Otherwise, it returns False.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.whitelist' decorator is used to allow guest access to the function.
- The 'frappe.db.get_single_value' function is used to retrieve the value of the 'tuna_enable' field.
"""
@frappe.whitelist(allow_guest=True)
def tuna_hms_enabled():
	return frappe.db.get_single_value("Sajha Menu Settings", "tuna_enable")

"""
Check if USB printing is enabled.

Returns:
- bool: True if USB printing is enabled, False otherwise.

Description:
This function checks if USB printing is enabled by retrieving the value of the 'usb_print' field from the 'Sajha Menu Settings' document using the 'frappe.db.get_single_value' function. If the value is True, it returns True. Otherwise, it returns False.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.db.get_single_value' function is used to retrieve the value of the 'usb_print' field from the 'Sajha Menu Settings' document.
"""
@frappe.whitelist(allow_guest=True)
def usb_print_enabled():
	return frappe.db.get_single_value("Sajha Menu Settings", "usb_print")

"""
Get KOT and BOT orders for a given table.

Parameters:
- table (str): The name of the table.

Returns:
- list: A list of dictionaries containing the KOT and BOT orders for the table.

Description:
This function retrieves the KOT (Kitchen Order Ticket) and BOT (Bar Order Ticket) orders for a given table. It first retrieves the table document using the 'frappe.get_doc' function. Then, for each order in the 'kot_bot' field of the table document, it checks if the order is a KOT or a BOT based on the presence of "KOT" in the ticket number. If it is a KOT, it retrieves the KOT document using the 'frappe.get_doc' function and retrieves the item details from the KOT items. If it is a BOT, it retrieves the BOT document and retrieves the item details from the BOT items.

For each item in the KOT or BOT, it appends a dictionary to the 'data' list containing the item code, quantity, and item name obtained from the 'frappe.db.get_value' function.

Finally, it appends a dictionary to the 'kot_bot' list containing the order ID, owner, ticket number, item category (KOT or BOT), order items, creation time, and remark. The creation time is formatted using the 'datetime.strftime' function.

The function returns the 'kot_bot' list containing the KOT and BOT orders for the table.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table, KOT, and BOT documents.
- The 'frappe.db.get_value' function is used to retrieve the item name based on the item code.
- The 'datetime.strftime' function is used to format the creation time of the KOT or BOT.
"""
@frappe.whitelist()
def get_table_kot_bot(table):
	doc = frappe.get_doc("Tables", table)
	kot_bot = []
	for order in doc.kot_bot:
		if "KOT" in order.ticket_number:
			ord = frappe.get_doc("Kitchen Orders", order.ticket_name)
			data = []

			for ko in ord.items:
				data.append({"item_code": ko.item_code, 'quantity': ko.quantity,
							'item_name': frappe.db.get_value("Item", ko.item_code, "item_name")})
			kot_bot.append({"ID": order.ticket_name,"table":ord.table_name, "owner": order.owner, "number": order.ticket_number, "itemCategory": "KOT",
						"order": data, "time": datetime.strftime(ko.creation, "%H:%M"), "remark": f"{ord.remark}"})
		else:
			ord = frappe.get_doc("Bar Orders", order.ticket_name)
			data = []
			for ko in ord.items:
				data.append({"item_code": ko.item_code, 'quantity': ko.quantity,
							'item_name': frappe.db.get_value("Item", ko.item_code, "item_name")})
			kot_bot.append({"ID": order.ticket_name, "table":ord.table_name, "owner": order.owner, "number": order.ticket_number, "itemCategory": "BOT",
						"order": data, "time": datetime.strftime(ko.creation, "%H:%M"), "remark": f"{ord.remark}"})
	return kot_bot

"""
View the bill for a given table.

Parameters:
- table (str): The name of the table.

Returns:
- dict: A dictionary containing the bill details.

Description:
This function retrieves the bill details for a given table. It first retrieves the table document using the 'frappe.get_doc' function. Then, for each order in the table, it retrieves the item details using the 'frappe.db.get_value' function and the 'frappe.get_doc' function. It also retrieves the tax template details using the 'frappe.get_doc' function.

Next, it checks if the item has any taxes associated with it. If it does, it retrieves the tax rate from the tax template details.

Finally, it appends the order details to the 'orders' list, including the item code, item name, item price, quantity, and tax rate. It also includes the total charges for the table. The function then returns a dictionary containing the 'orders' list and the 'total' charges.

Note:
- This function requires the 'frappe' module to be imported.
- The 'frappe.get_doc' function is used to retrieve the table document, item document, and subcategory item document.
- The 'frappe.db.get_value' function is used to retrieve the item price details.
- The 'frappe.get_doc' function is used to retrieve the item tax template details.
- The 'orders' list is used to store the order details.
- The 'append' method is used to add new order dictionaries to the 'orders' list.
"""
@frappe.whitelist(allow_guest=True)
def viewBill(table):
	table = frappe.get_doc("Tables", table)
	orders = []
	for order in table.orders:
		item = frappe.db.get_value("Item Price", {'item_code': order.item, 'selling': 1}, [
			'name', 'item_code', 'item_name', 'price_list_rate'], as_dict=1)
		itemTax = frappe.get_doc("Item", order.item)
		itemCategory = frappe.get_doc(
			"Sub Category Items", {"item_code": order.item})
		taxTemplate = None
		rate = 0.0
		if len(itemTax.taxes) > 0:
			taxTemplate = itemTax.taxes[0].item_tax_template

			dataTax = frappe.get_doc("Item Tax Template Detail", {
				"parent": f"{taxTemplate}"}, ignore_permissions=True)
			rate = dataTax.get("tax_rate")

		orders.append({'item': {"item_code": item['item_code'], "name": item['name'], 'item_name': item['item_name'], 'price_list_rate': (
			itemCategory.rate)}, 'qty': order.quantity, 'taxRate': rate})
	# return table

	return {'orders': orders, 'total': table.total_charges}

@frappe.whitelist(allow_guest = True)
def get_ssid_list():
	ssid_list = frappe.db.get_list("SSID Map", filters={'parent': 'Sajha Menu Settings'}, fields=['*'],ignore_permissions=True)
	enabled= frappe.db.get_single_value( "Sajha Menu Settings", 'enabled')

	frappe.local.response['data'] = {'enabled': enabled, 'ssidList': ssid_list}

@frappe.whitelist(allow_guest=True)
def get_floor_plan():
	try:
		floor = frappe.db.get_list("Floor Plan",ignore_permissions=True)
		data = []
		for f in floor:
			doc = frappe.get_cached_doc("Floor Plan", f['name'], ignore_permissions=True)
			floor={'name': doc.get('name'), 'tableList':[]}
			for d in doc.get('table_list'):
				floor['tableList'].append(d.table_name)
			data.append(floor)
		return data
	except Exception as e:
		return e

@frappe.whitelist(allow_guest=True)
def getFloorList(restaurant):
	return frappe.db.get_list('Floor List', {'parent': restaurant}, ['floor_name'], ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def estimate_enabled():
	return frappe.db.get_single_value("Sajha Menu Settings",'estimate_enabled')

@frappe.whitelist(allow_guest=True)
def maximum_discount():
	return frappe.db.get_single_value("Sajha Menu Settings",'maximum_discount')

@frappe.whitelist(allow_guest=True)
def create_sales_order():
	return frappe.db.get_single_value("Sajha Menu Settings",'sales_order')

@frappe.whitelist(allow_guest=True)
def get_print_name():
	return frappe.db.get_single_value("Sajha Menu Settings",'ird_print_name')

@frappe.whitelist(allow_guest=True)
def check_if_bill_exists(table):
	table = frappe.get_doc("Tables", table)
	if len(table.kot_bot) > 0:
		doc = frappe.db.get_value("KOT_BOT",{'ticket_name':table.kot_bot[0].ticket_name, 'parenttype': "Sales Invoice"}, "parent")
		if doc is not None:
			return {"code": "ALREADY_EXISTS", 'invoice': doc, "check": True}
		else:
			return {"code":"OK", "check":False}
	else:
		return {"code":"OK", "check":False}

@frappe.whitelist()
def check_opening_shift():
	is_opening = frappe.db.get_single_value("Sajha Menu Settings",'enable_opening')
	if is_opening:
		email = frappe.session.data.user
		company = frappe.db.get_value('User', email, 'company')
		opening = frappe.db.get_list("Cashier Summary", filters =[["Cashier Summary","closing_datetime","is","not set"],["Cashier Summary","company",'=',company]])
		if len(opening) > 0:
			return True
		else:
			return False
	else:
		return "Cashier Summary Disabled"

@frappe.whitelist()
def open_shift(amount):
	try:
		email = frappe.session.data.user
		company = frappe.db.get_value('User', email, 'company')
		opening = frappe.db.get_list("Cashier Summary",filters= [["Cashier Summary","closing_datetime","is","not set"],["Cashier Summary","company",'=',company]])
		if len(opening) > 0:
			return False
		else:
			doc = frappe.new_doc("Cashier Summary")
			doc.opening_amount = amount
			doc.opening_datetime = frappe.utils.now()
			doc.company = company
			doc.save()
			return True
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")
		return False

def get_invoice_details_cashier(opening, closing, company):
	s_data = []
	inv_list = frappe.db.sql("""
		SELECT
			name,
			status,
			grand_total,
			discount_amount,
			outstanding_amount
		FROM
			`tabSales Invoice`
		WHERE
			company = %s
			AND docstatus = 1
			AND creation BETWEEN %s AND %s
	""", (company, opening, closing), as_dict=True)


	payment_list = frappe.db.sql("""
		SELECT
			name
		FROM
			`tabPayment Entry`
		WHERE
			company = %s
			AND docstatus = 1
			AND creation BETWEEN %s AND %s
	""", (company, opening, closing), as_dict=True)

	s_data = {
		'no_of_sales':len(inv_list),
		'no_of_cash_sales':0,
		'no_of_credit_sales':0,
		'total_paid_sales':0,
		'total_credit_sales':0,
		'total_sales':0,
		'discount_amount':0,
		'cash_collection':0,
		'fonepay_collection':0,
		'esewa_collection':0,
		'other_collection':0,
  		'credit_cash_collection':0,
		'credit_fonePay_collection':0,
		'credit_esewa_collection':0,
		'credit_other_collection':0,
		'credit_collection':0,
		'total_collection':0,
	}
	for inv in inv_list:
		s_data['discount_amount'] += inv.discount_amount
		s_data['total_sales'] += inv.grand_total
		s_data['total_paid_sales'] += round((inv.grand_total - inv.outstanding_amount),0)
		s_data['total_credit_sales'] += inv.outstanding_amount
		if inv.status == "Paid":
			s_data['no_of_cash_sales']+= 1
		else:
			s_data['no_of_credit_sales']+= 1

	for payment in payment_list:
		paymentDoc = frappe.get_doc('Payment Entry',payment.name)
		if paymentDoc.payment_type == 'Receive':
			for item in paymentDoc.references:
				if item.reference_doctype == "Sales Invoice":
					s_data['total_collection'] += item.allocated_amount
					sales_creation = frappe.db.get_value('Sales Invoice', item.reference_name, 'creation')
					if opening > sales_creation:
						s_data['credit_collection'] += item.allocated_amount
						if 'FonePay' in paymentDoc.mode_of_payment:
							s_data['credit_fonePay_collection'] += item.allocated_amount
						elif  'Esewa' in paymentDoc.mode_of_payment:
							s_data['credit_esewa_collection'] += item.allocated_amount
						elif 'Cash' in paymentDoc.mode_of_payment:
							s_data['credit_cash_collection'] += item.allocated_amount
						else :
							s_data['credit_other_collection'] += item.allocated_amount
					elif paymentDoc.mode_of_payment is None:
						s_data['other_collection']+= item.allocated_amount
					elif 'FonePay' in paymentDoc.mode_of_payment:
						s_data['fonepay_collection'] += item.allocated_amount
					elif 'Esewa' in paymentDoc.mode_of_payment:
						s_data['esewa_collection'] += item.allocated_amount
					elif 'Cash' in paymentDoc.mode_of_payment:
						s_data['cash_collection']+= item.allocated_amount
					else:
						s_data['other_collection']+= item.allocated_amount
	return(s_data)

@frappe.whitelist()
def check_cashier_report():
	try:
		email = frappe.session.data.user
		company = frappe.db.get_value('User', email, 'company')
		register_list = frappe.db.get_list("Cashier Summary", filters=[["Cashier Summary","closing_datetime","is","not set"],["Cashier Summary","company",'=',company]], fields=['name'])
		if len(register_list) > 0:
			doc = frappe.get_doc("Cashier Summary", register_list[0]['name'])
			return {'company': company, 'opening_time':doc.opening_datetime, 'closing_time': frappe.utils.now(), 'opening_amount': doc.opening_amount, 'report': get_invoice_details_cashier(doc.opening_datetime, frappe.utils.now(), company)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")
		return False

@frappe.whitelist()
def close_register():
	try:
		email = frappe.session.data.user
		company = frappe.db.get_value('User', email, 'company')
		register_list = frappe.db.get_list("Cashier Summary", filters=[["Cashier Summary","closing_datetime","is","not set"],["Cashier Summary","company",'=',company]], fields=['name'])
		if len(register_list) > 0:
			doc = frappe.get_doc("Cashier Summary", register_list[0]['name'])
			doc.closing_datetime = frappe.utils.now()
			data = get_invoice_details_cashier(doc.opening_datetime, doc.closing_datetime, company)

			html_format = f"""
					<div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f4f4f4;">
						<div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
							<h1 style="text-align: center; color: #333; margin-bottom: 10px;">Daily Cashier Report</h1>
							<h2 style="text-align: center; color: #666; margin-top: 0; margin-bottom: 10px;">{company}</h2>
							<p style="text-align: center; color: #888; margin-bottom: 20px;">{doc.opening_datetime}</p>

							<div style="margin-bottom: 20px;">
								<p style="margin: 5px 0;"><strong>Opening Amount:</strong> Rs.{doc.opening_amount}</p>
								<p style="margin: 5px 0;"><strong>Closing Date:</strong>{doc.closing_datetime}</p>
							</div>

							<h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px; color: #444;">Sales Count</h3>
							<ul style="list-style-type: none; padding-left: 0; margin-top: 10px;">
								<li style="margin-bottom: 5px;"><strong>No of Sales:</strong>{data['no_of_sales']}</li>
								<li style="margin-bottom: 5px;"><strong>No of Cash Sales:</strong>{data["no_of_cash_sales"]}</li>
								<li style="margin-bottom: 5px;"><strong>No of Credit Sales:</strong>{data["no_of_credit_sales"]}</li>
							</ul>

							<h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px; color: #444;">Sales</h3>
							<ul style="list-style-type: none; padding-left: 0; margin-top: 10px;">
								<li style="margin-bottom: 5px;"><strong>Total Paid Sales:</strong> Rs.{data["total_paid_sales"]}</li>
								<li style="margin-bottom: 5px;"><strong>Total Credit Sales:</strong> Rs.{data["total_credit_sales"]}</li>
								<li style="margin-bottom: 5px;"><strong>Total Sales:</strong> Rs.{data["total_sales"]}</li>
								<li style="margin-bottom: 5px;"><strong>Discount Amount:</strong> Rs.{data["discount_amount"]}</li>
							</ul>

							<h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px; color: #444;">Collection</h3>
							<ul style="list-style-type: none; padding-left: 0; margin-top: 10px;">
								<li style="margin-bottom: 5px;"><strong>Cash Collection:</strong> Rs.{data["cash_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>FonePay Collection:</strong> Rs.{data["fonepay_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Esewa Collection:</strong> Rs.{data["esewa_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Other Collection:</strong> Rs.{data["other_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Cr. Cash Collection:</strong> Rs.{data["credit_cash_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Cr. FonePay Collection:</strong> {data["credit_fonePay_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Cr. Esewa Collection:</strong> Rs.{data["credit_esewa_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Cr. Other Collection:</strong> Rs.{data["credit_other_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Total Cr. Collection:</strong> Rs.{data["credit_collection"]}</li>
								<li style="margin-bottom: 5px;"><strong>Total Collection:</strong> Rs.{data["total_collection"]}</li>
							</ul>

							<h3 style="border-bottom: 1px solid #ddd; padding-bottom: 5px; color: #444;">Closing</h3>
							<p style="margin-top: 10px;"><strong>Total Cash Closing:</strong> Rs.{doc.opening_amount + data["cash_collection"] + data["credit_cash_collection"]}</p>

							<p style="text-align: center; margin-top: 20px; color: #888;">Thank You !</p>
						</div>
					</div>

   				"""
			doc.raw_data = html_format
			doc.save()
			frappe.db.commit()
			return {'company': company, 'opening_time':doc.opening_datetime, 'closing_time': doc.closing_datetime,  'opening_amount': doc.opening_amount, 'report': get_invoice_details_cashier(doc.opening_datetime, doc.closing_datetime, company)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"{e}")
		return False

@frappe.whitelist()
def sajha_notification_count():
	user = frappe.session.user
	userCompany = frappe.get_doc("User", user).get("company")
	return frappe.db.count("Sajha Notification", {"company":userCompany, "seen": 0})

@frappe.whitelist()
def sajha_notification():
	user = frappe.session.user
	userCompany = frappe.get_doc("User", user).get("company")
	data = frappe.db.get_list("Sajha Notification", filters={"company":userCompany}, fields=['name','notification', 'seen'], page_length =20 )
	return data

@frappe.whitelist()
def mark_as_seen():
	try:
		user = frappe.session.user
		userCompany = frappe.get_doc("User", user).get("company")

		data = frappe.db.get_list("Sajha Notification",filters={"company":userCompany, "seen":0})
		frappe.db.begin()
		for notify in data:
			frappe.db.set_value("Sajha Notification",notify.name,"seen", 1)
		frappe.db.commit()
		return data
	except Exception as e:
		frappe.db.rollback()
		return e


@frappe.whitelist()
def sajha_pos_settings():
	try:
		doc = frappe.get_doc("Sajha Menu Settings")
		return doc
	except Exception as e:
		return e

@frappe.whitelist()
def get_is_crm_customer(customer):
	if frappe.db.exists("DocType", "CRM Form"):
		data = frappe.db.get_value("CRM Form", {'c_name': customer}, 'name')
		return False if data is None else True
	return True
