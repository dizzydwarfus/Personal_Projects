//main.js
$(document).ready(function() {
    $('.select2').select2({
        tags: true,
        tokenSeparators: [',', ' ']
    });

    $('#expenseCategory').on('change', function() {
        console.log("Category change event triggered");
        var category = $(this).val();
        var encodedCategory = encodeURIComponent(category);
        console.log("Selected category: " + encodedCategory);
        $.getJSON('/get_subcategories/' + encodedCategory, function(data) {
            var subCategorySelect = $('#expenseSubCategory');
            subCategorySelect.empty();
            $.each(data, function(index, value) {
                subCategorySelect.append('<option value="' + value + '">' + value + '</option>');
            });
            subCategorySelect.trigger('change'); // Notify any JS components that the value changed
        });
    });

    $('.edit-btn').on('click', function() {
        var id = $(this).data('id');
        var description = $(this).data('description');
        var category = $(this).data('category');
        var subcategory = $(this).data('subcategory');
        var date = $(this).data('date');
        var cost = $(this).data('cost');

        $('#editExpenseModal').find('#expenseId').val(id);
        $('#editExpenseModal').find('#expenseDescription').val(description);
        $('#editExpenseModal').find('#expenseCategory').val(category);
        $('#editExpenseModal').find('#expenseSubCategory').val(subcategory);
        $('#editExpenseModal').find('#expenseDate').val(date);
        $('#editExpenseModal').find('#expenseCost').val(cost);

        var actionUrl = '/edit_expense/' + id;
        $('#editExpenseForm').attr('action', actionUrl);
        // Trigger the change event on category and subcategory fields
        $('#editExpenseModal #expenseCategory').trigger('change')
    });

    $('#editExpenseModal #expenseCategory').on('change', function() {
        var category = $(this).val();
        var encodedCategory = encodeURIComponent(category);
        $.getJSON('/get_subcategories/' + encodedCategory, function(data) {
            var subCategorySelect = $('#editExpenseModal #expenseSubCategory');
            subCategorySelect.empty();
            $.each(data, function(index, value) {
                subCategorySelect.append('<option value="' + value + '">' + value + '</option>');
            });
        });
    });

    // Toggle Add Expenses Form
    function toggleAddExpense() {
        var bracket = document.querySelector('.add-expense-bracket');
        var content = document.querySelector('.add-expense-content');

        if (bracket.classList.contains('expanded')) {
            bracket.classList.remove('expanded');
            content.style.display = 'none';
        } else {
            bracket.classList.add('expanded');
            content.style.display = 'block';
        }
    }

    let backgroundColors = [
        'rgba(255, 99, 132, 0.2)',    // Red
        'rgba(54, 162, 235, 0.2)',    // Blue
        'rgba(255, 206, 86, 0.2)',    // Yellow
        'rgba(75, 192, 192, 0.2)',    // Teal
        'rgba(153, 102, 255, 0.2)',   // Purple
        'rgba(255, 159, 64, 0.2)',    // Orange
        'rgba(255, 99, 255, 0.2)',    // Pink
        'rgba(255, 235, 59, 0.2)',    // Light Yellow
        'rgba(18, 203, 196, 0.2)',    // Light Teal
        'rgba(253, 167, 223, 0.2)',   // Light Pink
        'rgba(50, 255, 126, 0.2)',    // Lime
        'rgba(108, 52, 131, 0.2)',    // Dark Purple
        'rgba(72, 52, 212, 0.2)',     // Indigo
        'rgba(30, 144, 255, 0.2)',    // Dodger Blue
        'rgba(104, 255, 140, 0.2)'    // Light Green
    ];

    
    // Function to plot a pie chart of expenses by category
    function plotPieChart(categories, amounts) {
        // Assuming you already have a <canvas> element in your HTML with id="pieChart"
        let ctx = document.getElementById('pieChart').getContext('2d');
        let chart = new Chart(ctx, {
            // The type of chart we want to create
            type: 'pie',

            // The data for our dataset
            data: {
                labels: categories,
                datasets: [{
                    data: amounts,
                    // Add colors
                    backgroundColor: backgroundColors.slice(0, categories.length)
                }]
            },

            // Configuration options
            plugins: [ChartDataLabels],
            options: {
                plugins: {
                    tooltip: {
                        enabled: true,
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: '#FFFFFF', // Change to the color you want for the labels
                        },
                    },
                    datalabels: {
                        color: '#FFFFFF', // Change to the color you want for the data labels
                        formatter: function(value, context) {
                            return value == 0 ? '' : '€' + value.toFixed(2);
                        }
                    }
                }
            }
        });
    }

    // Function to plot a bar chart of expenses over time
    function plotBarChart(dates, amounts) {
        // Assuming you already have a <canvas> element in your HTML with id="barChart"
        let ctx = document.getElementById('barChart').getContext('2d');
        let chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Expenses',
                    data: amounts,
                    // Add colors
                    backgroundColor: [
                        // Add your colors here
                    ]
                }]
            },
            plugins: [ChartDataLabels],
            options: {
                plugins: {
                    tooltip: {
                        enabled: true,
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: '#FFFFFF', // Change to the color you want for the labels
                        },
                    },
                    datalabels: {
                        color: '#FFFFFF', // Change to the color you want for the data labels
                        anchor: 'end',
                        align: 'top',
                        formatter: function(value, context) {
                            return value == 0 ? '' : '€' + value.toFixed(2);
                        }
                    }
                }
            }
        });
    }

    // Function to plot a stacked bar chart of expenses over time by category
    function plotStackedBarChart(dates, categoryData) {
        // Ensure your categoryData is sorted in a specific order, so colors correspond to the same category across updates.
        for (let i = 0; i < categoryData.length; i++) {
            categoryData[i].backgroundColor = backgroundColors[i % backgroundColors.length];
        }
        // Assuming you already have a <canvas> element in your HTML with id="stackedBarChart"
        let ctx = document.getElementById('stackedBarChart').getContext('2d');
        let chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: categoryData
            },
            plugins: [ChartDataLabels],
            options: {
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true
                    }
                },
                plugins: {
                    tooltip: {
                        enabled: true,
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: '#FFFFFF', // Change to the color you want for the labels
                        },
                    },
                    datalabels: {
                        color: '#FFFFFF', // Change to the color you want for the data labels
                        anchor: 'end',
                        align: 'top',
                        formatter: function(value, context) {
                            return value == 0 ? '' : '€' + value.toFixed(2);
                        }
                    }
                }
            }
        });
    }

    // Function to plot a heatmap of expenses
    function plotHeatMap(dates, amounts) {
        // Implementation depends on the library you are using for the heatmap
    }

    // Retrieve the data from the chartData variable
    var categories = chartData.categories;
    var amounts = chartData.amounts;
    var dates = chartData.dates;
    var categoryData = chartData.categoryData;

    // Plotting the data
    plotPieChart(categories, amounts);
    plotBarChart(dates, amounts);
    plotStackedBarChart(dates, categoryData);
    plotHeatMap(dates, amounts);

});