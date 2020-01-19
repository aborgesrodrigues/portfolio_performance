    function getRandomColor() {
        var letters = '0123456789ABCDEF';
        var color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }


    $( document ).ready(
        function()
        {
            var $years_stock_history = $("#years_stock_history");
            var $years_portfolio_performance = $("#years_portfolio_performance");

            //create the options for the years drowdown
            $.each(years, function (key, value) {
                $years_stock_history.append($('<option></option>').attr('value', value).text(value));
                $years_portfolio_performance.append($('<option></option>').attr('value', value).text(value));
            });

            //Event for the update button of the stock history chart
            $("#update_stock_history").click(function(){
                var unit = $("#unit_stock_history").val();
                var year = $("#years_stock_history").val();

                data = stock_price_history_day_data;

                if(unit == "month")
                    data = stock_price_history_month_data;
                else if (unit == "year")
                    data = stock_price_history_year_data;

                chart_stock_price.config.data.datasets = get_stock_price_history_chart_dataset(data, year);
                chart_stock_price.update();
            });

            //Event for the change of the stock history unity chart
            $("#unit_stock_history").change(function() {
                $years_stock_history.show();

                if(this.value == "year") {
                    $years_stock_history.hide();
                    $years_stock_history.val("")
                }
            });

            //Event for the update button of the portfolio performance chart
            $("#update_portfolio_performance").click(function(){
                var unit = $("#unit_portfolio_performance").val();
                var year = $("#years_portfolio_performance").val();

                data = portfolio_performance_data;

                if(unit == "month")
                    data = portfolio_performance_month_data;
                else if (unit == "year")
                    data = portfolio_performance_years_data;

                var datasets_label = get_portfolio_performance_datasets(data, year);

                chart_portfolio_performance.config.data.labels = datasets_label[0];
                chart_portfolio_performance.config.data.datasets = datasets_label[1];
                chart_portfolio_performance.update();
            });

            //Event for the change of the portfolio performance unity chart
            $("#unit_portfolio_performance").change(function() {
                $years_portfolio_performance.show();

                if(this.value == "year") {
                    $years_portfolio_performance.hide();
                    $years_portfolio_performance.val("")
                }
            });

            //Create charts
            var chart_portfolio_performance = create_portfolio_performance_chart();
            var chart_stock_price = create_stock_price_history_chart();
        }
    );

//filter the data by year
function filter_data_by_year(data, year){
    var filtered_data = data;

    if(year != "") {
        filtered_data = filtered_data.filter(function (elem){
            return elem.x1.indexOf(year + "-") >= 0
        });
    }

    return filtered_data;
}

function get_stock_price_history_chart_dataset(data, year){
    var datasets = [];

    for(var key in data){
        if (data.hasOwnProperty(key)) {
            var color = getRandomColor();
            dataset = {
                label: key,
                backgroundColor: color,//.alpha(0.5).rgbString(),
                borderColor: color,
                data: filter_data_by_year(data[key], year),
                type: "line",
                pointRadius: 0,
                fill: false,
                lineTension: 0,
                borderWidth: 2
            }

            datasets.push(dataset);
        }
    }

    return datasets;
}

function create_stock_price_history_chart(){

    var ctx = document.getElementById('stock_price_history_chart').getContext('2d');
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;

    var color = Chart.helpers.color;
    var cfg = {
        data: {
            datasets: get_stock_price_history_chart_dataset(stock_price_history_day_data, "")
        },
        options: {
            animation: {
                duration: 0
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    distribution: 'series',
                    offset: true,
                    ticks: {
                        major: {
                            enabled: true,
                            fontStyle: 'bold'
                        },
                        source: 'data',
                        autoSkip: true,
                        autoSkipPadding: 75,
                        maxRotation: 0,
                        sampleSize: 100
                    }

                }],
                yAxes: [{
                    gridLines: {
                        drawBorder: false
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Closing price ($)'
                    }
                }]
            },
            tooltips: {
                intersect: false,
                mode: 'index',
                callbacks: {
                    label: function(tooltipItem, myData) {
                        var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += parseFloat(tooltipItem.value).toFixed(2);
                        return label;
                    }
                }
            }
        }
    };

    var chart = new Chart(ctx, cfg);
    return chart;
}

function get_portfolio_performance_datasets(data, year){
    var datasets = [];

    for(var key in data){

        if (data.hasOwnProperty(key)) {
            var filtered_data = filter_data_by_year(data[key], year);

            //Creating the labels for the chart
            var labels = []
            for(var item in filtered_data){
                labels.push(filtered_data[item].x);
            }

            var color = getRandomColor();
            dataset = {
				label: key,
				backgroundColor: color,
				data: filtered_data
            }


            datasets.push(dataset);
        }
    }

    return [labels, datasets];
}


function create_portfolio_performance_chart(){

    var ctx = document.getElementById('portfolio_performance_chart').getContext('2d');
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;

    var datasets_label = get_portfolio_performance_datasets(portfolio_performance_data, "");

    cfg = {
        type: 'bar',
        data: {
            labels: datasets_label[0],
            datasets: datasets_label[1],
        },
        options: {
            title: {
                display: true,
                text: 'Portfolio Performance'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(tooltipItem, myData) {
                        var label = myData.datasets[tooltipItem.datasetIndex].label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += parseFloat(tooltipItem.value).toFixed(2);
                        return label;
                    }
                }
            },
            responsive: true,
            scales: {
                xAxes: [{
                    stacked: true,
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        }
    };

    var chart = new Chart(ctx, cfg);
    return chart;
}