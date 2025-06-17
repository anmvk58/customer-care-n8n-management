$(function() {
    // Date Range picker
    $("input[name=\"daterange\"]").daterangepicker({
        opens: "left"
    });

    // Date Single picker
    $("input[name=\"datesingle\"]").daterangepicker({
        singleDatePicker: true,
        showDropdowns: true
    });
});

// Convert daterange to fromDate and toDate
function convertDateString(dateStr) {
    var dates = dateStr.split(' - ');

    function formatDate(date) {
        var [month, day, year] = date.split('/');
        return Number(year)*10000 + Number(month)*100 + Number(day);
    }

    return dates.map(formatDate)
}

// Convert date single to business_date
function convertDateSingle(dateStr) {
    var [month, day, year] = dateStr.split('/');
    return Number(year)*10000 + Number(month)*100 + Number(day);
}