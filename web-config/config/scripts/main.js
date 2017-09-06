// Add your javascript here
// Don't forget to add it into respective layouts where this js file is needed

var Password = findGetParameter('password');
// For testing!!
Password = 'unrar_angel';
// For testing!!
var dataOfLogging;
var dataOfWatchers;
var dataOfGlobals;

$(document).ready(function(){
    getLoggingInfo();
    getWatcherSettings();
    $pagenumber = $('#pagenumber');

    $("#amountonpage").bind('change', function() {
        $pagenumber.attr("data-val", 1);
        $pagenumber.attr("value", 1);
        $pagenumber.val(1);
        updateLogView();
    });
    $pagenumber.bind('change', function(){
        updateLogView();
    })
});


function getLoggingInfo(){
    var url = 'http://' + localIP + ":" + APIPort + "/logging/500?pass=" + Password;
    $.getJSON(url)
        .done(function (json) {
            dataOfLogging = json.data;
            var i = 0;
            $.each(json.data, function (i, log) {
                if (i < 10){
                    createTableRow(
                        $('.logging-home-page'),
                        log.time,
                        log.level,
                        log.component,
                        log.message
                    )
                }
            });
            updateLogView();
        })
        .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ", " + error;
                console.log( "Request Failed: " + err );
        });
}

function getWatcherSettings(){
    var amountOfWatchers = 0;
    var amountOfActiveWatchers = 0;
    var url = 'http://' + localIP + ":" + APIPort + "/all_watcher_settings?pass=" + Password;
    $.getJSON(url)
        .done(function (json) {
            dataOfWatchers = json;
            $.each(json, function (i, watcher) {
                amountOfWatchers++;
                if (watcher[1]['key'] == 1)
                    amountOfActiveWatchers++;
            });

            $('.watchers-in-total').text(amountOfWatchers);
            $('.running-watchers').text(amountOfActiveWatchers);
        })
        .fail(function( jqxhr, textStatus, error ) {
            var err = textStatus + ", " + error;
            console.log( "Request Failed: " + err );
        });
}

function updateLogView(){
    $pageNumber = $('#pagenumber');
    var whichPage = $pageNumber.attr("data-val");
    var amountOnPage = $('#amountonpage').attr("data-val");
    var startLog = amountOnPage * (whichPage - 1);
    var endLog = amountOnPage * whichPage;

    $tableBody = $('.log-page-table-body');
    $tableBody.empty();

    $pageList = $('.page-selector');
    $pageList.empty();
    var max = 500 / amountOnPage;
    console.log(max);
    for (var i = 1; i <= max; i++) {
        console.log('created');
        $li = $('<li>')
            .addClass('mdl-menu__item')
            .attr('data-val', i)
            .attr('tabindex', "-1")
            .text(i)
            .appendTo($pageList);
    }
    $($li).ready(function(){
        getmdlSelect.init('.getmdl-select');
    });


    for (i = startLog; i < endLog; i++) {
        log = dataOfLogging[i];
        if (!log)
            return;
        createTableRow(
            $tableBody,
            log.time,
            log.level,
            log.component,
            log.message
        )
    }
}

function closeSelectAndUpdateValue(val){
    $('.page-selector').hide();
    $pagenumber.attr("data-val", val);
    $pagenumber.attr("value", val);
    $pagenumber.val(val);
}

function createTableRow(appendTo, first, second, third, fourth){
    $tr = $('<tr>').appendTo(appendTo);
    row = [first, second, third, fourth];
    for (var i = 0; i < row.length; i++){
        $('<td>')
            .addClass('mdl-data-table__cell--non-numeric')
            .text(row[i])
            .appendTo($tr)
    }
}


function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
            tmp = item.split("=");
            if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    return result;
}