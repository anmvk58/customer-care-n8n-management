$(document).ready(function () {
    $("#search_event").click(function(){
        searchEvent()
    });
});


function searchEvent(){
    $('#loading-overlay').addClass('active').show();
    var input_date = $('#input_date').val();

    var input_company_name =  $('#company_name').val();
    var input_event_object =  $('#event_object').val();
    var input_event_type =  $('#event_type').val();


    if (input_company_name.trim() === '' && input_event_object.trim() === '' && input_event_type.trim() === ''){
        pushNotification('Cảnh báo', 'Vui lòng nhập ít nhất 1 thông tin', 'warning')
        $('#loading-overlay').removeClass('active');
        $('#loading-overlay').fadeOut(500);
        return
    }

    $.ajax({
            url: '/msb-event/filter-event',
            type: 'POST',
            data: JSON.stringify({
                company_name: "hana",
                event_object: "",
                event_type: "",
                event_date: 20250617
            }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getCookie('access_token')
            },
            success: function(response, status, xhr) {
                if (xhr.status === 200) {
                    console.log(response)
                    $("#event_data").empty();
                    response.data.forEach((item, index) => {
                        $("#event_data").append(
                        '<tr>' +
                            '<td>'  + (index + 1) + '</td>' +
                            '<td>'  + item.company_name + '</td>' +
                            '<td>'  + item.event_object + '</td>' +
                            '<td>'  + item.event_position + '</td>' +
                            '<td>'  + item.full_event + '</td>' +
                            '<td>'  + item.promt + '</td>' +
                            '<td>'  + item.received_email + '</td>' +
                            '<td>'  + item.is_active + '</td>' +
                            '<td>'  + item.is_loop + '</td>' +
                        '</tr>'
                        )
                    });
                    $('#bill_code').val("");
                    $('#cust_phone').val("");
                    $('#cust_name').val("");

                    pushNotification('Success', 'Tìm kiếm thành công', 'success');
                }
            },
            error: function(xhr, status, error) {
                console.error("Lỗi khi gọi API:", error);
                pushNotification('Failed', 'Tìm kiếm thất bại', 'error')
            }
    }).always(function(){
        $('#loading-overlay').removeClass('active');
        $('#loading-overlay').fadeOut(500);
    });
}
