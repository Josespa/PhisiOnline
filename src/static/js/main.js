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
    
})(jQuery);

