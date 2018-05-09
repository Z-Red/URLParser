# Monday, January 29, 2018
# Araien Redfern

# A URL parser that should behave close to urllib, however,
# does not contain any code to parse authority portion outside
# of the host and port.
#
# Copyright (C) 2018  Araien Redfern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#    
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#    
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs

# Parses a URL into its constituent components
def parse_url(url):

    # URL components
    scheme = None
    host = None
    port = None
    path_list = None
    query_dict = {}
    fragment = None

    # Get scheme
    scheme_ends = url.index(":")
    scheme = url[0:scheme_ends]

    # If there is only a scheme
    if (scheme_ends == len(url)-1):
        return (scheme, None, None, None, None, None)

    # Otherwise, get the starting indices of the URL components
    host_starts = scheme_ends + 3 
    port_starts = url.find(":", host_starts)
    path_starts = url.find("/", host_starts)
    query_starts = url.find("?")
    fragment_starts = url.rfind("#")

    # Get the host portion, if it exists, and decode it
    host = doHost(url, host_starts, path_starts, query_starts, fragment_starts)

    # Get port, if it exists
    if (port_starts < path_starts) and (port_starts != -1): 
        host = url[host_starts:port_starts]
        port = int(url[port_starts+1:path_starts])
        
    # Get the path, if it exists, and decode it
    path_list = doPath(url, path_starts, query_starts, fragment_starts)

    # Parse the query, if it exists, and decode it
    if (query_starts > -1):
        query_dict = doQuery(url, query_starts, fragment_starts)

    # Get fragment, if it exists, and decode it
    if (fragment_starts != -1) and (fragment_starts > query_starts):
        fragment = url[fragment_starts+1:]
        fragment = decodeString(fragment)

    return (
        scheme,
        host,
        port,
        path_list,
        query_dict,
        fragment
    )



# Takes a string that was percent encoded and percent-decodes it 
def decodeString(string):

    char_num = 0
    while (char_num < len(string)):
        if (string[char_num]) == '%' and (char_num < len(string)-2):

            only_ascii = True
            hx1 = string[char_num+1:char_num+3]
            hx2 = ''
            # If the following percent encoding will not decode to only ASCII
            if((string[char_num+1].upper() == 'C') or
              (string[char_num+1].upper() == 'D')):
                only_ascii = False
                hx2 = string[char_num+4:char_num+6]
            
            # Decode
            res = codecs.decode(hx1+hx2, 'hex_codec')
            res = res.decode('utf-8')

            # Contract string
            if (not only_ascii):
                string = string[:char_num] + res + string[char_num+6:]
            else:
                string = string[:char_num] + res + string[char_num+3:]
        char_num += 1

    return string


# Retrieves the host portion from a URL and returns it's percent-decoded string
def doHost(url, host_starts, path_starts, query_starts, fragment_starts):

        # If there is a path
        host = ''
        if (path_starts > -1):
            host = url[host_starts:path_starts]

        # If there is no path
        else:

            # If there is a query and no path
            if (query_starts > -1):
                host = url[host_starts:query_starts] 

            # Else if there is no query and no path but a fragment
            elif (fragment_starts > -1):
                host = url[host_starts:fragment_starts]

            # Else there was no query and no fragment AND no path
            else:
                host = url[host_starts:]

        return decodeString(host)


# Retrieves the path portion from a URL and returns its percent-decoded string
# list of components
def doPath(url, path_starts, query_starts, fragment_starts):

        # Get path
        query_string = ''

        # If there is no query and no frament
        if (query_starts == -1) and (fragment_starts == -1): 
            path = url[path_starts:]

        # If there is no query but a framents exists
        elif (query_starts == -1) and (fragment_starts != -1): 
            path = url[path_starts:fragment_starts]

        # If there is a query and maybe a fragment
        else:
            path = url[path_starts:query_starts]

            # If there is no fragment
            if (fragment_starts == -1) :
                query_string = url[query_starts+1:]

            # Else if a fragment exists
            else:
                query_string = url[query_starts+1:fragment_starts]
            
        # Parse path into list and decode each string element
        if (path_starts > 1):
            path_list = path.strip('/').split('/')
            string_num = 0
            for string in path_list:
                path_list[string_num] = decodeString(string)
                string_num += 1
        
        # Else if there was no path for some reason
        else:
            path_list = []

        return path_list



# Takes a url as a string along with the starting point of the query and the
# starting point of the fragment (if it exists) and returns a dictionary that
# contains key, value pairs relating the query components
def doQuery(url, query_starts, fragment_starts):

    # Get the query string from the url
    query_dict = {}
    query_string = ' '
    if (fragment_starts > -1):
        query_string = url[query_starts+1:fragment_starts]
    else:
        query_string = url[query_starts+1:]

    # Get key, value pairs of the query
    query_list = query_string.split('&')
    for string in query_list:

        char_num = 0
        for char in string:
            if (char == '='):
                k = string[:char_num]
                v = string[char_num+1:]

                if k in query_dict:
                    query_dict[k].append(v)
                else:
                    query_dict[k] = [v]
            char_num += 1
            
    # Decode the query components
    for k in query_dict:
        string_num = 0
        for string in query_dict[k]: 
            string = string.replace('+', ' ')
            query_dict[k][string_num] = decodeString(string.replace('+', ' '))
            string_num += 1

    return query_dict
