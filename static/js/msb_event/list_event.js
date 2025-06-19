$(document).ready(function () {
    searchEvent(true);

    $("#search_event").click(function(){
        searchEvent(false)
    });
});


function searchEvent(is_first){
    $('#loading-overlay').addClass('active').show();
    var input_date = $('#input_date').val();

    var input_company_name =  $('#company_name').val();
    var input_event_object =  $('#event_object').val();
    var input_event_type =  $('#event_type').val();

    if (!is_first){
        if (input_company_name.trim() === '' && input_event_object.trim() === '' && input_event_type.trim() === ''){
            pushNotification('Cảnh báo', 'Vui lòng nhập ít nhất 1 thông tin', 'warning')
            $('#loading-overlay').removeClass('active');
            $('#loading-overlay').fadeOut(500);
            return
        }
    }

    $.ajax({
            url: '/msb-event/filter-event',
            type: 'POST',
            data: JSON.stringify({
                company_name: input_company_name,
                event_object: input_event_object,
                event_type: input_event_type,
                event_date: convertDateSingle(input_date)
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
                            '<td>'  + item.event_type + '</td>' +
                            '<td>'  + item.full_event + '</td>' +
                            '<td>'  + item.promt + '</td>' +
                            '<td>'  + item.received_email + '</td>' +
                            '<td><span class="badge badge-' + (item.is_active == false ? 'danger"> Inactive </span></td>' : 'success"> Active </span></td>') +
                            '<td><span class="badge badge-' + (item.is_loop == false ? 'warning"> single-run </span></td>' : 'info"> Loop </span></td>') +
                            '<td>' +
                                '<a href="/msb-event/list-event/' + item.id + '"' +
                                '<i class="align-middle far fa-fw fa-edit"></i></a>' +
                            '</td>' +
                        '</tr>'
                        )
                    });

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
