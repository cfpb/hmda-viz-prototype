/**
    * get data for each select input
    * call the corresponding mustache template and fill the input
    * set the first option as selected
    */
function getUIData() {
    'use strict';
    $('select').each(function() {
        var selectID = this.id;
        // get <select> data
        $.get(selectID + '.json', function(data) {
            // sort on the name if its the msas
            if (selectID === 'msa-mds') {
                console.log('sorting');
                data['msa-mds'].sort(function(a,b) {
                    if(a.name < b.name) return -1;
                    if(a.name > b.name) return 1;
                    return 0;
                });
            }
            console.log(selectID);
            // get template
            $.get('/hmda-viz-prototype/templates/selects.html', function(templates) {
                var template = $(templates).filter('#' + selectID).html();
                var html = Mustache.to_html(template, data);
                $('#' + selectID).html(html);
                // set first option as selected
                $('#' + selectID + ' option:first').attr('selected', 'selected');
            });
        });
    });
}

/**
    * get data for the table
    * call the corresponding mustache template and fill the input
    * set the first option as selected
    */
function getTableData(table) {
    'use strict';
    var partials = {};

    // get <table> data
    $.get(table + '.json', function(data) {
        // add function to data to add commas to numbers
        // used in mustache templates as {#addCommas}}{{count}}{{/addCommas}}
        data["addCommas"] = function() {
            return function(number, render) {
                return render(number).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            }
        };
        console.log(data);
        // get the first charactire of the table #
        if (table.charAt(0) === '4') {
            table = '4';    // all 4's, 4-1 through 4-7, use the same table layout
        }
        // get partials
        $.get('/hmda-viz-prototype/templates/partials-tables.html', function(templates) {
            //var template = $(templates).filter('#' + table + '-new').html();
            partials['tablebanner'] = $(templates).filter('#tablebanner').html();
            //var html = Mustache.to_html(template, data);
        });
        // get template
        $.get('/hmda-viz-prototype/templates/' + table + '.html', function(templates) {
            //var template = $(templates).filter('#' + table + '-new').html();
            var template = $(templates).filter('#' + table).html();
            var html = Mustache.to_html(template, data, partials);
            $('#report').html(html);
        });
    });
}

/** 
    * update the button link on the form pages
    */
function setLink() {
    'use strict';
    var newURL = '';  // needed on first page, year and state make the url
    $('select').each(function() {
        newURL += $(this).val().replace(/ /g, '-').toLowerCase() + '/';
        console.log(newURL);
    });
    $('.js-btn').attr('href', newURL);
}

$( document ).ready(function() {
    'use strict';
    jQuery.ajaxSetup({async:false});  // no async!

    var urlPath = window.location.pathname.split('/');
    var path = urlPath[urlPath.length-2];
    console.log('length = ' + urlPath.length);
    if (urlPath.length === 8) {
        getTableData(path);
    } else if (urlPath.length === 6) {
        // fill the msa select inputs
        getUIData();
    }

    // initial set link
    setLink();
    // call setlink when new choice is made
    $('select').click(function() {
        setLink();
    });

    $('#print').click(function() {
        window.print();
    });

    // to csv
    // get the number of columns
    var colCount = 0;
    var theCSV = '';
    $('.report thead tr:first-child th').each(function () { // shouldn't rely on thead being there
        console.log ('im in');
        if ($(this).attr('colspan')) {
            colCount += +$(this).attr('colspan');
        } else {
            colCount++;
        }
    });

    theCSV = theCSV + '"' + $('#report-title').text() + '"' + '\n';
    theCSV = theCSV + '"' + $('#report-msa').text() + '"' + '\n';

    console.log (colCount);

    // loop through each row
    $('.report thead tr th, .report thead tr td, .report tbody tr td').each(function () {
        theCSV = theCSV + ('"' + $(this).text() + '"'); // put the content in first
        if ($(this).attr('colspan')) {
            for (var i = 0; i < +$(this).attr('colspan')-1; i++) {  // add extra columns
                theCSV = theCSV + ',';
            }
        }
        if ($(this).is(':last-child')) {
            theCSV = theCSV + '\n';
        } else {
            theCSV = theCSV + ',';
        }
    });

    $('#csv').click(function() {
        window.open('data:text/csv;charset=utf-8,' + escape(theCSV));
    });
});