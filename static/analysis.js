function ui(name){
    return document.getElementById(name);
}
ui("loader").style.display = "none";
ui("loader1").style.display = "none";
ui("second").style.display = "none";
ui("third").style.display = "none";
ui("footer").style.display = "none";
ui("btn1").addEventListener("click", function(){
    ui("footer").style.display = "block";
    ui("btn1").style.display = "none";
    ui("loader").style.display = "block";
    fetch('http://127.0.0.1:5300/api/category_distribution')
      .then(response => response.json())
      .then(data => {
        ui("first").style.display = "none";
        ui("second").style.display = "flex";
        ui("hh1").innerHTML = "Distributions";
        ui("hh1").style.padding = "1rem"
        ui("hh1").style.fontWeight= "600"
        document.body.style.backgroundColor = "#F0F0F0	";
        console.log(data)
        var options = {
      series: data.values, // Category values
      chart: {
        type: 'polarArea',
        width:  600,  // Set custom width
        height: 600  
      },
      labels: data.labels, // Add category labels
      stroke: {
        colors: ['#fff']
      },
      fill: {
        opacity: 0.8
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 10
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    };
          var pieChart = new ApexCharts(document.querySelector("#pieChart"), options);
          pieChart.render();
      });

})

ui("ss1").addEventListener("click", function(){
    ui("grp2").style.display = "none";
    ui("loader1").style.display = "block";
    var skill = document.getElementById("s1").value;
    if(!skill) {
        alert("Please enter a skill");
        return;
      }
      fetch('http://127.0.0.1:5300/api/candidate_rankings?skill=' + encodeURIComponent(skill))
      .then(response => response.json())
        .then(results => {
            ui("loader1").style.display = "none";
            ui("grp2").style.display = "none";
            ui("grp1").style.display = "block";
            ui("third").style.display = "block";

          // Prepare data for bar chart (candidate IDs and match scores)
          var candidateIDs = results.slice(0, 10).map(r => String(r.ID));
          console.log(candidateIDs)
          var matchScores = results.slice(0,10).map(r => r.Match_Score);

          var options = {
          series: [{
          data: matchScores
        }],
          chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            borderRadius: 4,
            borderRadiusApplication: 'end',
            horizontal: true,
          }
        },
        dataLabels: {
          enabled: false
        },
        xaxis: {
          title: {
      text: 'Score'
    },
          categories: candidateIDs,
          labels: {
        formatter: (value) => {
          return value.toFixed(1)
        },
      }
        }
        };

          var barChart = new ApexCharts(document.querySelector("#barChart"), options);
          barChart.render();
        });

})
document.getElementById("btn3").addEventListener("click", function () {
  ui("btn3").innerHTML = "Generating..";
    const skill = ui("s1").value;
    if (!skill) return;

    fetch(`http://127.0.0.1:5300/api/generate_ranked_candidates?skill=${encodeURIComponent(skill)}`)
        .then(response => response.json())
        .then(data => {
          ui("btn3").innerHTML = "Download";
            if (data.download_url) {
                // Create an invisible link, trigger the download, then remove it
                const tempLink = document.createElement("a");
                tempLink.href = data.download_url;
                tempLink.download = "ranked_candidates.txt";
                document.body.appendChild(tempLink);
                tempLink.click();
                document.body.removeChild(tempLink);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    })