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
            create_portfolio_performance_chart();
            create_stock_price_history_chart();


        }
    );

function create_stock_price_history_chart(){

    var datasets = [];

    for(var key in stock_price_history_day_data){
        if (stock_price_history_day_data.hasOwnProperty(key)) {
            var color = getRandomColor();
            dataset = {
                label: key,
                backgroundColor: color,//.alpha(0.5).rgbString(),
                borderColor: color,
                data: stock_price_history_day_data[key],
                type: "line",
                pointRadius: 0,
                fill: false,
                lineTension: 0,
                borderWidth: 2
            }

            datasets.push(dataset);
        }
    }


    var ctx = document.getElementById('stock_price_history_chart').getContext('2d');
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;



    var color = Chart.helpers.color;
    var cfg = {
        data: {
            datasets: datasets
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

}


function create_portfolio_performance_chart(){
    var datasets = [];


    for(var key in portfolio_performance_data){

        if (portfolio_performance_data.hasOwnProperty(key)) {
            //Creating the labels for the chart
            var labels = []
            for(var item in portfolio_performance_data[key]){
                labels.push(portfolio_performance_data[key][item].x);
            }

            var color = getRandomColor();
            dataset = {
				label: key,
				backgroundColor: color,
				data: portfolio_performance_data[key]
            }


            datasets.push(dataset);
        }
    }

    var ctx = document.getElementById('portfolio_performance_chart').getContext('2d');
    ctx.canvas.width = 1000;
    ctx.canvas.height = 300;

    cfg = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            title: {
                display: true,
                text: 'Portfolio Performance'
            },
            tooltips: {
                mode: 'index',
                intersect: false
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

}