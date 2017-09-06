/**
 * Created by Administrator on 06-Sep-17.
 */

// Menu classes (this does not contain all pages as some of them are only accessible part of the time)
// (e.g. the training form, this is only accessible during one month of the training season)
var listWithMenuItems = [
    ".menu-home", ".menu-global", ".menu-watcher", ".menu-log"
];
// Content classes
var listWithAllContentItems = [
    ".home-page", ".global-config-page", ".watcher-config-page", ".log-page"
];
// How the hash is called in the url
var listWithLinkNames = [
    "home", "global-config", "watcher-config", "logging"
];

$(document).ready(function () {
    hashChangeCurrentView();
});

// Support for link paramater. so http://url.com#config/param where config is page name and param is a possible param.
var linkParam = null;
function getLinkParam(){
    return linkParam;
}

// Getting the URL information, linkName contains which div to open and linkParam contains a variable.
function hashChangeCurrentView(){
    var url = window.location.href;
    url = url.substr(url.indexOf("#") + 1);
    var linkName = url.substr(0,url.indexOf('/'));
    if(linkName.length==0){
        linkName = url;
    }
    // This can be used for example #activity/2213, then 2213 is the linkParam
    linkParam = url.substr(url.indexOf('/')+1);
    linkParam = linkParam.replace('/', '');

    // Here we change the view depending on the hash.
    var indexOfLink = $.inArray(linkName, listWithLinkNames);
    if(indexOfLink != -1 && indexOfLink < listWithMenuItems.length) {
        changeView(listWithMenuItems[indexOfLink], listWithAllContentItems[indexOfLink]);
    } else {
        changeView(".home-page",listWithAllContentItems[0]);
    }
}

// Function for changing the view. Easy to do this in one function.
function changeView(menuItemSelected, theNewView) {
    selectMenuItem(menuItemSelected);
    slideUp(theNewView);
}

function selectMenuItem(menuItemSelected) {
    for (var i = 0; i < listWithMenuItems.length; i++) {
        $(listWithMenuItems[i]).removeClass("fel-selected");
    }

    for (i = 0; i < listWithMenuItems.length; i++) {
        if (menuItemSelected == listWithMenuItems[i]) {
            $(listWithMenuItems[i]).addClass("fel-selected");
        }
    }
}

// This is the function which opens or closes all the dashboard divs.
function slideUp(toBeShown) {
    // We load a new javascript file
    /*var indexOfToBeShown = listWithAllContentItems.indexOf(toBeShown);
     if(firstLoad[indexOfToBeShown]){
     var url = "js/pages/"+listWithJSFileToLoad[indexOfToBeShown];
     $.getScript(url);
     firstLoad[listWithAllContentItems.indexOf(toBeShown)] = false;
     }*/

    // We hide each element in the list.
    listWithAllContentItems.forEach(function (divName) {
        if (toBeShown != divName && $(divName).is(":visible")) {
            $(divName).hide(0);
        }
    });
    // We show the new element in the list
    listWithAllContentItems.forEach(function (divName) {
        if (toBeShown == divName && !$(divName).is(":visible")) {
            $(divName).show();
        }
    });
}

