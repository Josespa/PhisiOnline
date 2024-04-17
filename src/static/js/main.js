(function ($) {
    "use strict";

    
    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });

    var $select_physio = $( '#select_physio' ),
		    $select_time = $('#select_time'),
        $select_date = $( '#select_date' ),
        $info_physio = $( '#info_physio' ),
        $options = $info_physio.find( 'div' );
    
    $select_physio.on( 'change', function() {
        var physio_id = $select_physio.val();
        var date = $select_date.val();
        $info_physio.html( $options.filter( '[value="' + this.value + '"]' ) );
        if (physio_id != "" && date!= "") {
            load_data(physio_id, date);
        }
    } ).trigger( 'change' );

    $select_date.on( 'change', function() {
        var physio_id = $select_physio.val();
        var date = $select_date.val();
        if (physio_id != "" && date!= "") {
            load_data(physio_id, date);
        }
    } ).trigger( 'change' );

    function load_data(physio_id, date) {
                    
        $.ajax({
            url: "/availability",
            method: "POST",
            data: { physio_id: physio_id, date: date },
            dataType: "json",
            success: function (data) { //alert(category_id)
                var html = "";
                for (var count = 0; count < data.length; count++) {
                    html += '<option value="' + data[count].id + '">' + data[count].name + "</option>";
                }
                $("#select_time").html(html);
                $("#select_time").selectpicker("refresh");
                $date_select(html);
                $date_select("refresh");
                
            },
        });
    }

    var $updateselect_date = $( '#updateselect_date' ),
        $updateselect_physio = $( '#updateselect_physio');

    
    $updateselect_date.on( 'change', function() {
        var physio_id = $updateselect_physio.val();
        var date = $updateselect_date.val();
        if (physio_id != "" && date!= "") {
            load_data2(physio_id, date);
        }
        
    } ).trigger( 'change' );

    function load_data2(physio_id, date) {
                    
        $.ajax({
            url: "/availability",
            method: "POST",
            data: { physio_id: physio_id, date: date },
            dataType: "json",
            success: function (data) { //alert(category_id)
                var html = "";
                for (var count = 0; count < data.length; count++) {
                    html += '<option value="' + data[count].id + '">' + data[count].name + "</option>";
                }
                $("#updateselect_time").html(html);
                $("#updateselect_time").selectpicker("refresh");
                $updateselect_date(html);
                $updateselect_date("refresh");
                
            },
        });
    }


    var $select_datetime_off = $( '#select_datetime_off' );
    
    $select_datetime_off.on( 'change', function() {
        var date = $select_datetime_off.val();
        if (date!= "") {
          load_data_timeoff(date);
      }
    } ).trigger( 'change' );

    
    function load_data_timeoff(date) {
      $.ajax({
          url: "/availability_timeoff",
          method: "POST",
          data: { date: date },
          dataType: "json",
          success: function (data) { //alert(category_id)
              var html = "";
              for (var count = 0; count < data.length; count++) {
                  html += '<option value="' + data[count].id + '">' + data[count].name + "</option>";
              }
              $("#select_timeoff").html(html);
              $("#select_timeoff").selectpicker("refresh");
              $select_datetime_off(html);
              $select_datetime_off("refresh");
              
          },
      });
  }

  var $select_category = $( '#select_category' ),
		  $select_exercise = $('#select_exercise'),
      $info_exercise = $( '#info_exercise' ),
      $options_exercises = $info_exercise.find( 'div' );;
    
    $select_category.on( 'change', function() {
        var category_id = $select_category.val();
        load_data_category(category_id);
    } ).trigger( 'change' );

    $select_exercise.on( 'change', function() {
      $info_exercise.html( $options_exercises.filter( '[value="' + this.value + '"]' ) );
  } ).trigger( 'change' );
    
    function load_data_category(category_id) {
                    
      $.ajax({
          url: "/exercises_category",
          method: "POST",
          data: { category_id },
          dataType: "json",
          success: function (data) { //alert(category_id)
              var html = "";
              for (var count = 0; count < data.length; count++) {
                  html += '<option value="' + data[count].id + '">' + data[count].name + "</option>";
              }
              $("#select_exercise").html(html);
              $("#select_exercise").selectpicker("refresh");
              $select_category(html);
              $select_category("refresh");
              
          },
      });
    }
    
      
      const ctx2 = document.getElementById("chart2").getContext('2d');
      const myChart2 = new Chart(ctx2, {
        type: 'bar',
        data: {
          labels: months,
          datasets: [{
            label: '2024',
            backgroundColor: 'rgba(161, 198, 247, 1)',
            borderColor: 'rgb(47, 128, 237)',
            data: appointments_months,
          }]
        },
        options: {
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero: true,
              }
            }]
          }
        },
      });
    
})(jQuery);

