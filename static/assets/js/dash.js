new Chart(document.getElementById("bar-chart"), {
	type: 'bar',
	data: {
		labels: {{ name | safe}},
	datasets: [
	{
		label: "Profit(Ksh)",
		backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
		data: {{ profit_product | safe}}
			}
	, {
		label: "Sales(Ksh.)",
		backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
		data: {{ sale_product | safe}}
			}

]
	},
	options: {
	legend: { display: false },
	title: {
		display: true,
		text: 'Profit and Sales per product'
	}
}
});

new Chart(document.getElementById("line-chart"), {
	type: 'line',
	data: {
		labels: {{ day_prof | safe}},
	datasets: [{
		data: {{ prof_day | safe}},
	label: "Profit",
	borderColor: "#3e95cd",
	fill: false
		}, {
		data: {{ sal_d | safe}},
	label: "Sales",
	borderColor: "#8e5ea2",
	fill: false
		}
]
	},
	options: {
	title: {
		display: true,
		text: 'Profit and Sales per day'
	}
}
});