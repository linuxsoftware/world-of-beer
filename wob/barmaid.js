// The World of Beer Barmaids

$(document).ready(function() {
    WorldOfBeerBarmaid.loadCookie();
    $("#barmaid").draggable({scroll: false,
                             cursor: 'move',
                             start:  function() {$(this).css('right', 'auto')},
                             stop:   WorldOfBeerBarmaid.saveCookie
                            });
    $("#banner").dblclick(WorldOfBeerBarmaid.callBarmaid);
    $('.topMenu a.barmaidLink').click(WorldOfBeerBarmaid.callBarmaid);
    $('#barmaid .closeLink').click(function() {
        $("#barmaid").hide();
        WorldOfBeerBarmaid.deleteCookie();
    });
    $('#barmaid').dblclick(function() {
        $("#barmaid").hide();
        WorldOfBeerBarmaid.deleteCookie();
    });
});

var WorldOfBeerBarmaid = new function()
{
    this.loadCookie = function()
    {
        var barmaidImg = $("#barmaid img.forSizingOnly");
        var rememberHer = jQuery.cookie('world-of-beer-barmaid');
        if (rememberHer == null) {
            var id = Math.ceil(Math.random()*17);
            var imgName = "/wob/barmaid_"+id+".jpg";
            barmaidImg.attr("src", imgName);
        } else {
            var herxy = rememberHer.split(',');
            var imgName = "/wob/barmaid_"+herxy[0]+".jpg";
            barmaidImg.attr("src", imgName);
            $("#barmaid").css({'right': 'auto',
                               'left':  herxy[1]+'px',
                               'top':   herxy[2]+'px',
                               'display': 'block',
                               'background-image': 'url('+imgName+')'
                              });
        }
    }

    this.saveCookie = function()
    {
        var barmaidImg = $("#barmaid img.forSizingOnly");
        var gotId = barmaidImg.attr('src').match(/barmaid_(\d+).jpg/);
        var id = 1;
        if (gotId) {
            id = gotId[1];
        }
        var position = $("#barmaid").position();
        var value = id+','+position.left+','+position.top;
        jQuery.cookie('world-of-beer-barmaid', value, {path:'/'});
    }

    this.deleteCookie = function()
    {
        jQuery.cookie('world-of-beer-barmaid', null, {path:'/'});
    }

    this.callBarmaid = function()
    {
        // will call out a new barmaid, or bring the current one to the top
        var barmaid = $("#barmaid");
        if (barmaid.css('display') == 'none') {
            var id = 1;
            var barmaidImg = $("#barmaid img.forSizingOnly");
            var gotId = barmaidImg.attr('src').match(/barmaid_(\d+).jpg/);
            if (gotId) {
                id = (parseInt(gotId[1]) % 17) + 1;
            }
            imgName = "/wob/barmaid_"+id+".jpg";
            barmaidImg.attr("src", imgName);
            barmaid.css({'display':          'block',
                         'background-image': 'url('+imgName+')'});
        }
        barmaid.css({'top':   '16px',
                     'left':  'auto',
                     'right': '26px'});
        WorldOfBeerBarmaid.saveCookie();

        return false;
    }
}


/*****************************************************************************/
/**
 * Cookie plugin
 *
 * Copyright (c) 2006 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */

/**
 * Create a cookie with the given name and value and other optional parameters.
 *
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Set the value of a cookie.
 * @example $.cookie('the_cookie', 'the_value', { expires: 7, path: '/', domain: 'jquery.com', secure: true });
 * @desc Create a cookie with all available options.
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Create a session cookie.
 * @example $.cookie('the_cookie', null);
 * @desc Delete a cookie by passing null as value. Keep in mind that you have to use the same path and domain
 *       used when the cookie was set.
 *
 * @param String name The name of the cookie.
 * @param String value The value of the cookie.
 * @param Object options An object literal containing key/value pairs to provide optional cookie attributes.
 * @option Number|Date expires Either an integer specifying the expiration date from now on in days or a Date object.
 *                             If a negative value is specified (e.g. a date in the past), the cookie will be deleted.
 *                             If set to null or omitted, the cookie will be a session cookie and will not be retained
 *                             when the the browser exits.
 * @option String path The value of the path atribute of the cookie (default: path of page that created the cookie).
 * @option String domain The value of the domain attribute of the cookie (default: domain of page that created the cookie).
 * @option Boolean secure If true, the secure attribute of the cookie will be set and the cookie transmission will
 *                        require a secure protocol (like HTTPS).
 * @type undefined
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */

/**
 * Get the value of a cookie with the given name.
 *
 * @example $.cookie('the_cookie');
 * @desc Get the value of a cookie.
 *
 * @param String name The name of the cookie.
 * @return The value of the cookie.
 * @type String
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */
jQuery.cookie = function(name, value, options) {
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } else { // only name given, get cookie
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

/*****************************************************************************/

