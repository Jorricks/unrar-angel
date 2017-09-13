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
    $('.getmdl-select-which-config').bind('change', function(){
        updateWatcherConfigForm();
    });
    $pagenumber.bind('change', function(){
        updateLogView();
    });
    $('#add-new-watcher-button').on('click', function(){
        addNewWatcherConfig();
    });
    $('.watcher-config-page .custom-fab').on('click', function(){
        var retVal = confirm("Are you sure you want to remove this config ?");
        if( retVal == true ){
            removeCurrentWatcherConfig();
        }
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

var currentWatcherUID = '';
function getWatcherSettings(){
    var amountOfWatchers = 0;
    var amountOfActiveWatchers = 0;
    var url = 'http://' + localIP + ":" + APIPort + "/all_watcher_settings?pass=" + Password;
    $.getJSON(url)
        .done(function (json) {
            dataOfWatchers = json;
            var first = true;
            $.each(json, function (i, watcher) {
                if(first){
                    first = false;
                    currentWatcherUID = watcher[0]['value'];
                }
                amountOfWatchers++;
                if (watcher[1]['value'] == 1)
                    amountOfActiveWatchers++;
            });

            getWatcherConfig(json);
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
var watcherJson = '';
function getWatcherConfig(json){
    if(json != undefined){
        watcherJson = json;
    }
    $wachterselecter = $('.watcher-config-selecter-div');


    $li = '';
    $watcherconfigul = $('.watcher-ul-select');
    $.each(watcherJson, function (i, watcher) {
        $li = $('<li>')
            .addClass('mdl-menu__item')
            .attr('data-val', watcher[0]['value'])
            .attr('tabindex', "-1")
            .text(watcher[2]['value'])
            .appendTo($watcherconfigul);
    });
    $($li).ready(function(){
        getmdlSelect.init('.getmdl-select-which-config');
    });

    updateWatcherConfigForm();
}

function updateWatcherConfigForm(){
    $watcherconfigform = $('.watcher-config-form');
    $watcherconfigform.empty();
    buildForm(watcherJson[currentWatcherUID], $watcherconfigform, getWatcherTrans);

    // addSeperatorAfterElementDad($('#copy_or_unrar'));
    addSeperatorAfterElementDad($('#unrar_not_rar_but_match_regexp'));
    addSeperatorAfterElementDad($('#recursive_directory_building_for_new_file'));
    addSeperatorAfterElementDad($('#plex_library_name'));

    ifOnDisableFriends($('#plex_on_or_off'), 'plex');

    basedOnResultDisable($('#copy_or_unrar'), 'copy', 'unrar');
}

function addSeperatorAfterElementDad($item){
    $seperator = $('<div>')
        .addClass('watcher-separator');
    $item.parent().after($seperator);
}

function ifOnDisableFriends($item, selector){
    $item.bind("change", function(e){
        if($item.parent().hasClass('is-checked')){
            $( "input[id^='" + selector + "']" ).prop("disabled", false);
        } else {
            $( "input[id^='" + selector + "']" ).prop("disabled", true);
            $item.prop("disabled", false);
        }
    });
    $item.trigger("change");
}

function basedOnResultDisable($item, selector1, selector2){
    $item.bind("change", function(e){
        if($item.val() == selector1){
            $( "input[id^='" + selector1 + "']" ).parent().show();
            $( "input[id^='" + selector2 + "']" ).parent().hide();
        } else {
            $( "input[id^='" + selector1 + "']" ).parent().hide();
            $item.parent().show();
            $( "input[id^='" + selector2 + "']" ).parent().show();
        }
    });
    $item.trigger("change");
}


function getGlobalConfig(){
    var url = 'http://' + localIP + ":" + APIPort + "/global_settings?pass=" + Password;
    $.getJSON(url)
        .done(function (json) {
            buildForm(json, $('.global-config-form'), getGlobalTrans);
        })
        .fail(function( jqxhr, textStatus, error ) {
            var err = textStatus + ", " + error;
            console.log( "Request Failed: " + err );
        });
}

function buildForm(jsonData, $form, translatefunction, prefix){
    if(prefix == undefined)
        prefix = '';
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
                .text(translatefunction(element.name))
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

            $input = $('<input>')
                .attr('type', 'checkbox')
                .attr('id', prefix + element.name)
                .addClass('mdl-switch__input')
                .appendTo($label);

            if(element.value == 1)
                $input.attr('checked', true);

            $('<span>')
                .addClass('mdl-switch__label')
                .text(translatefunction(element.name))
                .appendTo($label);

            upgradeEl($label);
            if(element.name == 'on_or_off'){
                $label.prependTo($form);
            } else {
                $label.appendTo($form);
            }
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
                .attr('readonly', true)
                .attr('tabIndex', '-1')
                .attr('data-val', element.value);
            upgradeEl($input);
            $input.appendTo($formElement);

            $label = $('<label>')
                .addClass('mdl-textfield__label')
                .attr('for', prefix + element.name)
                .text(translatefunction(element.name));
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

            // Removing the last empty list item.. Weird shit.
            $('li', $ul).last().remove();
        }
    });
}

function addNewWatcherConfig(){
    return false;
}

function removeCurrentWatcherConfig(){
    return false;
}

function submitGlobalForm(){
    var data = {};
    var textfields = document.forms["globalConfig"].getElementsByTagName("input");
    for(var i = 0; i < textfields.length; i++){
        data[textfields[i].id] = textfields[i].value;
    }
    var url = 'http://' + localIP + ":" + APIPort + "/global_settings";
    updateSettings(data, "global_settings", url);
}

function submitWatcherForm(){
    var data = {};
    var textfields = document.forms["watcherConfig"].getElementsByTagName("input");
    for(var i = 0; i < textfields.length; i++){
        if (textfields[i].value == 'on' || textfields[i].value == 'off'){
            data[textfields[i].id] = textfields[i].checked;
        } else {
            data[textfields[i].id] = textfields[i].value;
        }
    }
    var url = 'http://' + localIP + ":" + APIPort + "/watcher_settings/"+data['uid'];
    updateSettings(data, "watcher_settings", url);
}

function updateSettings(newData, id, url){
    var data = {};
    data['pass'] = Password;
    data[id] = newData;
    data2 = JSON.stringify(data);
    $.ajax({
        type: 'POST',
        url: url,
        data: data2,
        success: function(data){console.log(data); alert('Update successful.');},
        error: function(data){console.log(data); alert('Something went wrong. Please restart the service.');},
        dataType: 'json',
        contentType : 'application/json',
        processData: false
    });
}




function upgradeEl($item){
    componentHandler.upgradeElement($item.get(0));
}

function getWatcherTrans(key){
    return returnWatcherTranslation()[key];
}

function getGlobalTrans(key){
    return returnGlobalTranslation()[key];
}

function returnGlobalTranslation(){
    var array = [];
    array["personal_name"] = "Your name";
    array["program_name"] = "Name of the program";
    array["logging_path"] = "Logging path";
    array["logging_path_new_files"] = "Logging path for second file";
    array["logging_level"] = "Logging level; debug logs everything";
    array["angel_pid_path"] = "Path of the daemon file(required in order to stay alive)";
    array["update_delay_in_seconds"] = "Check for an update every x seconds";
    array["web_config_site_port"] = "Port used for the config site";
    array["web_config_api_port"] = "Port used for the API of the config site";
    array["web_password"] = "Password required for accessing this site";
    return array;
}

function returnWatcherTranslation(){
    var array = [];
    array["uid"] = "The unique identifier. (Changing this will make a copy)";
    array["on_or_off"] = "Enable/disable this watcher";
    array["name"] = "Name of the watcher";
    array["source_path"] = "The folder the watcher should check for new files";
    array["destination_path"] = "The destination path of all the new files";
    array["copy_or_unrar"] = "Should we copy or unrar the files";
    array["remove_after_finished"] = "Remove the file after the operation has been done(remove after copy turns the operation into a move, way faster!))";
    array["copy_match_everything"] = "For copy operations, match everything(otherwise regexp below)";
    array["copy_not_everything_but_match_regexp"] = "The regexp the files should match too in order to be processed";
    array["unrar_match_only_rar_extension"] = "For rar operations, match .rar files(otherwise regexp below).";
    array["unrar_not_rar_but_match_regexp"] = "The regexp the rar files should match too in order to be proccesed";
    array["recursive_searching"] = "Search deep/recursive into the source path";
    array["recursive_directory_building_for_new_file"] = "Recursive directory building for the new file";
    array["plex_on_or_off"] = "Update plex libraries on succeed";
    array["plex_ip_port"] = "Plex library address (e.g. localhost:32400)";
    array["plex_token"] = "Your plex token (google 'get my plex token')";
    array["plex_library_name"] = "Plex library name (e.g. 'TV Series')";
    return array;
}

function getWatcherGroups(){

}