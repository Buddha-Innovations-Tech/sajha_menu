frappe.pages['test-page'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Test',
		single_column: true
	});

	page.set_title('My Page')
	page.set_indicator('Pending', 'orange')
	page.clear_indicator()
	let $btn = page.set_primary_action('New', () => create_new(), 'octicon octicon-plus')
	let $btn2 = page.set_secondary_action('Refresh', () => refresh(), 'octicon octicon-sync')
	page.add_menu_item('Send Email', () => open_email_dialog())
	page.add_menu_item('Send Email', () => open_email_dialog(), true)
	page.add_action_item('Delete', () => delete_items())
	page.add_inner_button('Update Posts', () => update_posts())
	page.add_inner_button('New Post', () => new_post(), 'Make')
	page.add_inner_button('Delete Post', () => delete_post(), 'Make')
	page.change_inner_button_type('Update Posts', null, 'primary');
	page.change_inner_button_type('Delete Posts', 'Actions', 'danger')
	let field = page.add_field({
		label: 'Status',
		fieldtype: 'Select',
		fieldname: 'status',
		options: [
			'Open',
			'Closed',
			'Cancelled'
		],
		change() {
			console.log(field.get_value());
		}
	});
	let values = page.get_form_values()
	console.log(values)
}