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
                //console.log('sorting');
                // do to upper first
                $.each(data['msa-mds'], function(index, value) {
                    value.name = value.name.toUpperCase();
                });
                // sort
                data['msa-mds'].sort(function(a,b) {
                    if(a.name < b.name) return -1;
                    if(a.name > b.name) return 1;
                    return 0;
                });
            }
            //console.log(selectID);
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
        data['addCommas'] = function() {
            return function(number, render) {
                return render(number).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            }
        };
        data['footnote'] = function() {
            return function(string, render) {
                var footnote = 0;
                var footnote2 = 0;
                var footnote3 = 0;
                var footnoteurl = '/hmda-viz-prototype/footnotes/' + data.year + '/#';
                var url = '';
                console.log(render(string).toLowerCase());

                switch (render(string).toLowerCase()) {
                    case 'race':
                        footnote = 5;
                        break;
                    case 'not available':
                    case 'ethnicity not available':
                    case 'income not available':
                    case 'race not available':
                        footnote = 6;
                        break;
                    case 'ethnicity':
                        footnote = 7;
                        break;
                    case 'minority status':
                        footnote = 8;
                        break;
                    case 'applicant income':
                    case 'income of applicants':
                        footnote = 9;
                        break;
                    case 'racial&#x2f;ethnic composition':
                    case 'race&#x2f;ethnic composition':
                        footnote = 11;
                        break;
                    case 'income':
                    case 'income characteristics':
                        footnote = 12;
                        footnote2 = 13;
                        break;
                    case 'income &amp; racial&#x2f;ethnic composition':
                        footnote = 11;
                        footnote2 = 12;
                        footnote3 = 13;
                        break;
                    case 'total':
                        footnote = 14;
                        break;
                    case 'no reported pricing data':
                        footnote = 15;
                        break;
                    case 'all other tracts':
                        footnote = 21;
                        break;
                    case 'mean':
                        footnote = 30;
                        break;
                    case 'median':
                        footnote = 31;
                        break;
                    default:
                        footnote = 0;
                        footnote2 = 0;
                        footnote3 = 0;
                }

                // return
                if (footnote != 0) {
                    url = render(string) + ' <a href="' + footnoteurl + footnote + '"><sup>' + footnote + '</sup></a>';
                    if (footnote2 != 0) {
                        url = url + ' <a href="' + footnoteurl + footnote2 + '"><sup>' + footnote2 + '</sup></a>';
                    }
                    if (footnote3 != 0) {
                        url = url + ' <a href="' + footnoteurl + footnote3 + '"><sup>' + footnote3 + '</sup></a>';
                    }
                    console.log (url);
                    return url;
                }
                else {
                    return render(string);
                }
            }
        }
        //console.log(data);
        // get the first charactire of the table #
        if (table.charAt(0) === '4') {
            table = '4';    // all 4's, 4-1 through 4-7, use the same table layout
        }
        if (table.charAt(0) === '5') {
            table = '5';    // all 5's, 5-1 through 5-7, use the same table layout
        }
        if (table.charAt(0) === '7') {
            table = '7';    // all 7's, 7-1 through 7-7, use the same table layout
        }
        // get partials
        // table banner
        $.get('/hmda-viz-prototype/templates/partials-tables.html', function(templates) {
            //var template = $(templates).filter('#' + table + '-new').html();
            partials['tablebanner'] = $(templates).filter('#tablebanner').html();
            //var html = Mustache.to_html(template, data);
        });
        // table date
        $.get('/hmda-viz-prototype/templates/partials-tables.html', function(templates) {
            //var template = $(templates).filter('#' + table + '-new').html();
            partials['tabledate'] = $(templates).filter('#tabledate').html();
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
        //console.log(newURL);
    });
    $('.js-btn').attr('href', newURL);
}

$( document ).ready(function() {
    'use strict';
    jQuery.ajaxSetup({async:false});  // no async!

    var urlPath = window.location.pathname.split('/');
    var path = urlPath[urlPath.length-2];
    //console.log('length = ' + urlPath.length);
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
        //console.log ('im in');
        if ($(this).attr('colspan')) {
            colCount += +$(this).attr('colspan');
        } else {
            colCount++;
        }
    });

    theCSV = theCSV + '"' + $('#report-title').text() + '"' + '\n';
    theCSV = theCSV + '"' + $('#report-msa').text() + '"' + '\n';

    //console.log (colCount);

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

    function detectIE() {
        var ua = window.navigator.userAgent;

        var msie = ua.indexOf('MSIE ');
        if (msie > 0) {
            // IE 10 or older => return version number
            return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
        }

        var trident = ua.indexOf('Trident/');
        if (trident > 0) {
            // IE 11 => return version number
            var rv = ua.indexOf('rv:');
            return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
        }

        var edge = ua.indexOf('Edge/');
        if (edge > 0) {
           // IE 12 => return version number
           return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
        }

        // other browser
        return false;
}

    $('#csv').click(function() {
        //console.log(detectIE());
        if (detectIE() === false) {
            console.log('no ie');
            window.open('data:text/csv;charset=utf-8,' + escape(theCSV));
        } else {
            console.log('no ie');
            var blob = new Blob([theCSV], {type: 'text/csv'});
            navigator.msSaveOrOpenBlob(blob, 'strings.csv');
            /*theCSV = decodeURIComponent(theCSV);

            var iframe = document.getElementById('csvDownloadFrame');
            iframe = iframe.contentWindow || iframe.contentDocument;

            theCSV = 'sep=,\r\n' + theCSV;

            iframe.document.open("text/html", "replace");
            iframe.document.write(theCSV);
            iframe.document.close();
            iframe.focus();

            iframe.document.execCommand('SaveAs', true, 'data.csv');
            
            var oWin = window.open();
            oWin.document.write('sep=,\r\n' + theCSV);
            oWin.document.close();
            oWin.document.execCommand('SaveAs', true, fileName + ".csv");
            oWin.close();*/
        }
    });
});