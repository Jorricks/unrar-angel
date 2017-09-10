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
    });

    getGlobalConfig();
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
    for (var i = 1; i <= max; i++) {
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

/*
 *
 * Global config items
 *
 */

function getGlobalConfig(){
    var url = 'http://' + localIP + ":" + APIPort + "/global_settings?pass=" + Password;
    $.getJSON(url)
        .done(function (json) {
            buildForm(json, $('.global-config-form'));
        })
        .fail(function( jqxhr, textStatus, error ) {
            var err = textStatus + ", " + error;
            console.log( "Request Failed: " + err );
        });
}

function buildForm(jsonData, $form, prefix){
    $form.empty();
    $.each(jsonData, function (i, element) {
        if (element.type == "str" || element.type == "path" || element.type == "int"){
            $formElement = $('<div>')
                .addClass('mdl-textfield mdl-js-textfield mdl-textfield--floating-label');

            $input = $('<input>')
                .addClass('mdl-textfield__input')
                .attr('type', 'text')
                .prop('required',true)
                .attr('id', prefix + element.name)
                .val(element.value)
                .appendTo($formElement);

            $label = $('<label>')
                .addClass('mdl-textfield__label')
                .attr('for', prefix + element.name)
                .text(getGlobalTrans(element.name))
                .appendTo($formElement);

            $span = $('<span>')
                .addClass('mdl-textfield__error')
                .appendTo($formElement);

            if (element.type == "int") {
                $input.attr('pattern', "[0-9]+");
                $span.text('This should be a number!');
            }
            if (element.type == "str") {
                $input.attr('pattern', ".{1,}");
                $span.text('This should be a str!');
            }
            if (element.type == "path") {
                $input.attr('pattern', "(\/)(.{1,})");
                $span.text('This should be an absolute path!');
            }

            upgradeEl($formElement);
            $formElement.appendTo($form);
        }

        if(element.type == "bool"){
            $label = $('<label>')
                    .addClass('mdl-switch mdl-js-switch mdl-js-ripple-effect')
                    .attr('for', prefix + element.name);

            $('<input>')
                .attr('type', 'checkbox')
                .attr('id', prefix + element.name)
                .addClass('mdl-switch__input')
                .appendTo($label);

            $('<span>')
                .addClass('mdl-switch__label')
                .text(getGlobalTrans(element.name))
                .appendTo($label);

            upgradeEl($label);
            $label.appendTo($form);
        }

        if(element.type == "option"){
            $formElement = $('<div>')
                .addClass('getmdl-select__fullwidth ' +
                    'mdl-textfield mdl-js-textfield mdl-textfield--floating-label getmdl-select'+element.name);

            $input = $('<input>')
                .addClass('mdl-textfield__input')
                .attr('id', prefix + element.name)
                .attr('name', prefix + element.name)
                .attr('value', element.value)
                .attr('type', 'text')
                // .attr('readonly', 1)
                .attr('tabIndex', '-1')
                .attr('data-val', element.value);
            upgradeEl($input);
            $input.appendTo($formElement);

            $label = $('<label>')
                .addClass('mdl-textfield__label')
                .attr('for', prefix + element.name)
                .text(getGlobalTrans(element.name));
            upgradeEl($label);
            $label.appendTo($formElement);

            $ul = $('<ul>')
                .addClass('mdl-menu mdl-menu--bottom-left mdl-js-menu')
                .attr('for', prefix + element.name);
            // upgradeEl($ul);
            $ul.appendTo($formElement);

            for (var j = 0; j <= element.enum.length ; j++) {
                $li = $('<li>')
                    .addClass('mdl-menu__item')
                    .attr('data-val', element.enum[j])
                    .attr('tabindex', "-1")
                    .text(element.enum[j])
                    .appendTo($ul);
            }

            upgradeEl($formElement);
            $formElement.appendTo($form);

            getmdlSelect.init('.getmdl-select'+element.name);
        }
    });
}

function upgradeEl($item){
    componentHandler.upgradeElement($item.get(0));
}





function getGlobalTrans(key){
    return returnGlobalTranslation()[key];
}

function returnGlobalTranslation(){
    var array = [];
    array["personal_name"] = "Your name";
    array["program_name"] = "Name of the program";
    array["logging_path"] = "Logging path";
    array["logging_level"] = "Logging level; debug logs everything";
    array["angel_pid_path"] = "Path of the daemon file(required in order to stay alive)";
    array["update_delay_in_seconds"] = "Check for an update every x seconds";
    array["web_config_site_port"] = "Port used for the config site";
    array["web_config_api_port"] = "Port used for the API of the config site";
    array["web_password"] = "Password required for accessing this site";
    return array;
}