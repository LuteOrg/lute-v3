document.addEventListener('DOMContentLoaded', function() {
    fetch('/stats/data')
      .then(response => response.json())
      .then(data => {
        renderLineChart(data);
        renderDoughnutChart(data);
      });
  });

  function renderDoughnutChart(data) {
    var ctx = document.getElementById('languageDistributionChart').getContext('2d');

    const palette = [
      '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3',
      '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd'
    ];

    let labels = [];
    let chartData = [];
    let backgroundColors = [];
    let colorIndex = 0;

    Object.entries(data).forEach(entry => {
      const [langname, langdata] = entry;
      if (langdata.length > 0) {
        labels.push(langname);
        const totalWords = langdata[langdata.length - 1].runningTotal;
        chartData.push(totalWords);
        backgroundColors.push(palette[colorIndex % palette.length]);
        colorIndex++;
      }
    });

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: chartData,
          backgroundColor: backgroundColors,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Word Distribution by Language'
          }
        }
      }
    });
  }

  function renderLineChart(data) {
    var ctx = document.getElementById('wordCountChart').getContext('2d');

    const palette = [
      '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3',
      '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd'
    ];

    datasets = [];
    let colorIndex = 0;

    Object.entries(data).forEach(entry => {
      const [langname, langdata] = entry;
      const color = palette[colorIndex % palette.length];
      colorIndex++;

      var daily = {
        label: `${langname} (daily)`,
        yAxisID: 'daily',
        data: [],
        borderWidth: 1,
        type: 'bar',
        backgroundColor: color,
        borderColor: color,
      };

      var total = {
        label: `${langname} (total)`,
        yAxisID: 'total',
        data: [],
        borderWidth: 2,
        type: 'line',
        pointRadius: 0,
        borderColor: color,
        backgroundColor: 'transparent',
      };

      langdata.forEach(item => {
        daily.data.push({x: item.readdate, y: item.wordcount});
        total.data.push({x: item.readdate, y: item.runningTotal});
      });

      datasets.push(daily);
      datasets.push(total);
    });

    new Chart(ctx, {
      type: 'bar',
      data: {
        datasets: datasets
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Word Count Over Time'
          },
          legend: {
            position: 'top',
          },
        },
        scales: {
          x: {
            type: 'time',
            display: true,
            time: {
              unit: 'day',
              round: 'day'
            },
            title: {
              display: true,
              text: 'Date'
            },
            ticks: {
              major: {
                enabled: true
              },
            }
          },
          daily: {
            position: 'left',
            title: {
              display: true,
              text: 'Daily Count',
            },
            grid: {
              display: false
            },
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return value.toLocaleString();
              }
            }
          },
          total: {
            position: 'right',
            title: {
              display: true,
              text: 'Running Total',
            },
            grid: {
              display: false
            },
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return value.toLocaleString();
              }
            }
          },
        }
      }
    });
  }
