frappe.pages['food-delivery-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Food Delivery Dashboard',
		single_column: true
	});

	// Load data
	frappe.call({
		method: 'food_delivery.food_delivery.page.food_delivery_dashboard.food_delivery_dashboard.get_dashboard_data',
		callback: function(r) {
			if (r.message) {
				render_dashboard(page, r.message);
			}
		}
	});
}

function render_dashboard(page, data) {
	// Render stats
	var stats = data.today_stats;
	var html = `
		<div class="row">
			<div class="col-md-3">
				<div class="card">
					<div class="card-body">
						<h5>Today's Orders</h5>
						<h3>${stats.total_orders || 0}</h3>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card">
					<div class="card-body">
						<h5>Delivered</h5>
						<h3>${stats.delivered || 0}</h3>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card">
					<div class="card-body">
						<h5>Active</h5>
						<h3>${stats.active || 0}</h3>
					</div>
				</div>
			</div>
			<div class="col-md-3">
				<div class="card">
					<div class="card-body">
						<h5>Revenue</h5>
						<h3>₹${stats.revenue || 0}</h3>
					</div>
				</div>
			</div>
		</div>
	`;
	
	$(page.body).html(html);
}
