/**
 * A convenience function that allows you to declaratively emit multiple fields
 * for a single document in your map function.
 *
 * emit_array({
 *      data: {'foo': 0, 'bar': 1, 'baz': 1},
 *      key: ['a', 'b'],
 *      extra_keys: {'baz': ['c']}
 * });
 *
 * will result in the following under the hood:
 *
 * emit(['a', 'b', 'foo'], 0);
 * emit(['a', 'b', 'bar'], 1);
 * emti(['a', 'b', 'baz', 'c'], 1);
 *
 * @param options.data hash of data keys and number, boolean, or
 *        list<number,boolean> values for those keys
 * @param options.key
 * @param options.extra_keys hash of data keys and arrays of extra values to
 *        include in the key for that data key
 */
function emit_array(options) {
    var data = options.data,
        key = options.key,
        extra_keys = options.extra_keys || {};

    for (var k in extra_keys) {
        if (typeof extra_keys[k] !== "object") {
            extra_keys[k] = [extra_keys[k]];
        }
    }

    for (var k in data) {
        if (data[k] !== null) {
            var _emit = function (val) {
                var this_key = key.concat([k]).concat(extra_keys[k] || []);
                emit(this_key, val);
            };

            switch (typeof data[k]) {
            case 'boolean':
                _emit(data[k] ? 1 : 0);
                break;
            case 'object':  // array of numbers
                for (var i in data[k]) {
                    _emit(data[k][i]);
                }
                break;
            case 'number':
            default:
                _emit(data[k]);
                break;
            }
        }
    }
}
