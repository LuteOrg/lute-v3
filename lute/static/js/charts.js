document.addEventListener('DOMContentLoaded', function() {
    fetch('/stats/data')
      .then(response => response.json())
      .then(data => {
        renderLineChart(data.wordcount, data.timetracking);
        renderDoughnutChart(data.wordcount);
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
  }

function renderLineChart(wordCountData, timeData) {
    var ctx = document.getElementById('wordCountChart').getContext('2d');

    const palette = [
      '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3',
      '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd'
    ];

    let datasets = [];
    let colorIndex = 0;

    Object.entries(wordCountData).forEach(entry => {
      const [langname, langdata] = entry;
      const color = palette[colorIndex % palette.length];
      colorIndex++;

      var daily = {
        label: `${langname} (daily words)`,
        yAxisID: 'daily',
        data: [],
        borderWidth: 1,
        type: 'bar',
        backgroundColor: color,
        borderColor: color,
      };

      var total = {
        label: `${langname} (total words)`,
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

    const timeDataset = {
        label: 'Minutes Read',
        yAxisID: 'time',
        data: timeData.map(item => ({ x: item.date, y: item.minutes })),
        type: 'bar',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
    };
    datasets.push(timeDataset);

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
            text: 'Reading History'
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
              text: 'Daily Word Count',
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
              text: 'Running Total Words',
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
          time: {
            position: 'right',
            title: {
              display: true,
              text: 'Minutes Read'
            },
            grid: {
              drawOnChartArea: false,
            },
            ticks: {
              beginAtZero: true
            }
          }
        }
      }
    });
}