$(document).ready(function () {
    $("#btn-create-event").click(function(){
        createEvent()
    });

    $("#btn-preview-event").click(function(){
        previewEvent()
    });


    $('#event_type').on('change', function () {
    const selectedValue = $(this).val();

    if (selectedValue === 'ACTIVE_DATE') {
        $('#object_label').text("Khoản tiền được phê duyệt");
        $('#event_object').attr("placeholder", "2000000000");

        $('#title_label').text("Tần suất");
        $('#event_title').attr("placeholder", "Mặc định");

        $('#position_label').text("Đơn vị");
        $('#event_position').attr("placeholder", "Ngày");
    } else {
        $('#object_label').text("Tên đối tượng");
        $('#event_object').attr("placeholder", "Vũ Hà Phương");

        $('#title_label').text("Danh xưng");
        $('#event_title').attr("placeholder", "Bà");

        $('#position_label').text("Chức vụ");
        $('#event_position').attr("placeholder", "Giám đốc");
    }

  });

});


function createEvent(){
    $('#loading-overlay').addClass('active').show();

    var company_name = $('#company_name').val();
    var event_object = $('#event_object').val();
    var event_title = $('#event_title').val();
    var event_position = $('#event_position').val();
    var event_type = $('#event_type').val();
    var input_date = $('#input_date').val();
    var received_email = $('#received_email').val();
    var is_loop = $('#is_loop').is(':checked'); // true/false
    var promt = $('#promt').val();


    if (company_name.trim() === '' && event_object.trim() === '' && event_title.trim() === '' && event_position.trim() === '' ){
        pushNotification('Cảnh báo', 'Vui lòng nhập đủ thông tin', 'warning')
        $('#loading-overlay').removeClass('active');
        $('#loading-overlay').fadeOut(500);
        return
    }

    $.ajax({
            url: '/msb-event/create-event',
            type: 'POST',
            data: JSON.stringify({
                company_name: company_name,
                event_object: event_object,
                event_title: event_title,
                event_position: event_position,
                event_type: event_type,
                input_date: convertDateSingle(input_date),
                received_email: received_email,
                is_loop: is_loop,
                promt: promt
            }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getCookie('access_token')
            },
            success: function(response, status, xhr) {
                if (xhr.status === 200 || xhr.status === 201) {
                    console.log(response)

                    $('#company_name').val("");
                    $('#event_object').val("");
                    $('#event_title').val("");
                    $('#event_position').val("");
                    $('#event_type').val("");
                    $('#received_email').val("");
                    $('#promt').val("");

                    pushNotification('Success', 'Tạo sự kiện thành công', 'success');
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

function previewEvent(){
    $('#loading-overlay').addClass('active').show();

    var company_name = $('#company_name').val();
    var event_object = $('#event_object').val();
    var event_title = $('#event_title').val();
    var event_position = $('#event_position').val();
    var event_type = $('#event_type').val();
    var input_date = $('#input_date').val();
    var received_email = $('#received_email').val();
    var is_loop = $('#is_loop').is(':checked'); // true/false
    var promt = $('#promt').val();


    if (company_name.trim() === '' && event_object.trim() === '' && event_title.trim() === '' && event_position.trim() === '' ){
        pushNotification('Cảnh báo', 'Vui lòng nhập đủ thông tin', 'warning')
        $('#loading-overlay').removeClass('active');
        $('#loading-overlay').fadeOut(500);
        return
    }

    $.ajax({
            url: '/msb-event/preview-event',
            type: 'POST',
            data: JSON.stringify({
                company_name: company_name,
                event_object: event_object,
                event_title: event_title,
                event_position: event_position,
                event_type: event_type,
                input_date: convertDateSingle(input_date),
                received_email: received_email,
                is_loop: is_loop,
                promt: promt
            }),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getCookie('access_token')
            },
            success: function(response, status, xhr) {
                if (xhr.status === 200 || xhr.status === 201) {
                    console.log(response)
                    $('#event_header').html('<img src="/static/img/email/header_email.png">');

                    $('#event_preview').html(response.data.body_html);

                    $('#event_footer').html('<img src="/static/img/email/footer_email.png">');

                    pushNotification('Success', 'Xem trước sự kiện thành công', 'success');

                }
            },
            error: function(xhr, status, error) {
                console.error("Lỗi khi gọi API:", error);
                pushNotification('Failed', 'Kết nối lỗi, Vui lòng thử lại', 'error')
            }
    }).always(function(){
        $('#loading-overlay').removeClass('active');
        $('#loading-overlay').fadeOut(500);
    });
}
