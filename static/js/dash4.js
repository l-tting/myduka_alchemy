new Chart(document.getElementById("bar-chart"), {
    type: 'bar',
    data: {
        labels: {{ name | safe}},
    datasets: [
    {
        label: "Profit (KSH.)",
        backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
        data: {{ profit | safe}}
    },
    {
        label: "Sales (KSH.)",
        backgroundColor: ["#3e95cd", "#8e5ea2", "#3cba9f", "#e8c3b9", "#c45850"],
        data: {{ pro_sales | safe}}
    }
]
},
    options: {
    legend: { display: false },
    title: {
        display: true,
        text: 'PROFIT PER PRODUCT'
    }
}
});


new Chart(document.getElementById("line-chart"), {
    type: 'line',
    data: {
        labels: {{ day | safe}},
    datasets: [{
        data: {{ d_profit | safe}},
    label: "Profit",
    borderColor: "#FF0000",
    fill: false
        },
    {
        data: {{ sales_prod | safe}},
    label: "Sales",
    borderColor: "#3e95cd",
    fill: false
        },

]
    },
    options: {
    title: {
        display: true,
        text: 'PROFIT PER DAY(KSH.)'
    }
}
});