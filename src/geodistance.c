#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

static const double equatorial_radius = 6378.137; //km
static const double polar_radius = 6356.752;      //km

#define deg2rad(x) (M_PI * (x) / 180)

/*
 * Compute the distance between two points on earth using the Haversine formula
 * cf: http://en.wikipedia.org/wiki/Haversine_formula
 */
static void haversine(sqlite3_context *context, int argc, sqlite3_value **argv)
{
    assert(argc == 4);

    double  lat1 = deg2rad(sqlite3_value_double(argv[0]));
    double long1 = deg2rad(sqlite3_value_double(argv[1]));
    double  lat2 = deg2rad(sqlite3_value_double(argv[2]));
    double long2 = deg2rad(sqlite3_value_double(argv[3]));
    
    double  dlat = fabs(lat1 - lat2);
    double dlong = fabs(long1 - long2);
    
    /*  */
    double angle = 2 * asin(
        sqrt(pow(sin(dlat/2), 2) + 
             cos(lat1) * cos(lat2) * pow(sin(dlong/2), 2)));

    double res = angle * (equatorial_radius + polar_radius)/2;
    return sqlite3_result_double(context, res);
}

int sqlite3_geodistance_init(
    sqlite3 *db,
    char **errMsg,
    const sqlite3_api_routines *pApi
){
    SQLITE_EXTENSION_INIT2(pApi);
    
    /* Register function geodistance(lat1,long1, lat2,long2) -> km,
       standard encoding, bound to C func haversine(), with no supplementary
       data or aggregate function pointers */
    return sqlite3_create_function(db, "geodistance", 4, SQLITE_UTF8, NULL,
                                   haversine, NULL, NULL);
}
