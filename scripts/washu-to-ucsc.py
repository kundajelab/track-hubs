import json
import argparse

def convert_color(color):
    if color == 'red':
        return '255,0,0'
    elif color == 'green':
        return '0,255,0'
    elif color == 'blue':
        return '0,0,255'
    else:
        raise Exception(
            f"Color {color} not defined. Please add the RGB value to convert_color")


def convert_track(track):
    '''
    Performs the conversion of a single track from WashU to UCSC for all common
    fields of tracks.
    '''
    new_track = []
    new_track.append(['track', '_'.join(track['name'].split())])
    new_track.append(['bigDataUrl', track['url']])
    new_track.append(['shortLabel', track['name']])
    new_track.append(['longLabel', track['name']])
    new_track.append(['color', convert_color(track['options']['color'])])
    if track['showOnHubLoad']:
        new_track.append(['visibility', 'full'])
    return new_track


def convert_bigwig_windowing(washu_agg_fn):
    '''
    Converts WashU's aggregation function to UCSC's windowing function.
    '''
    if washu_agg_fn == 'MEAN':
        return 'mean'
    elif washu_agg_fn == 'MAX':
        return 'maximum'
    elif washu_agg_fn == 'MIN':
        return 'minimum'
    else:
        raise Exception(
            f"Aggregation function {washu_agg_fn} does not have a counterpart in UCSC. \
              See: https://genome.ucsc.edu/goldenPath/help/trackDb/trackDbHub.html#bigWig_-_Signal_Graphing_Track_Settings")


def convert_bigwig(track):
    new_track = convert_track(track)
    new_track.append(['type', 'bigWig'])
    new_track.append(['maxHeightPixels', '72:48:32'])
    if 'options' in track.keys() and 'aggregateMethod' in track['options'].keys():
        new_track.append(['windowingFunction',
                          convert_bigwig_windowing(track['options']['aggregateMethod'])])
    return new_track


def convert_dynseq(track):
    new_track = convert_track(track)
    new_track.append(['type', 'bigWig'])
    new_track.append(['logo', 'on'])
    new_track.append(['autoScale', 'on'])
    new_track.append(['alwaysZero', 'on'])
    new_track.append(['maxHeightPixels', '72:48:32'])
    return new_track


def convert_bed(track):
    new_track = convert_track(track)
    new_track.append(['type', 'bed'])
    return new_track


def process_track(track):
    if track['type'] == 'bigwig':
        return convert_bigwig(track)
    elif track['type'] == 'dynseq':
        return convert_dynseq(track)
    elif track['type'] == 'bed':
        return convert_bed(track)
    else:
        raise Exception(
            f"Track type {track['type']} does not have a defined conversion function.")


def process_tracks(tracks):
    output = ''
    for track in tracks:
       output += '\n'.join([' '.join(x) for x in process_track(track)]) + '\n\n'
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converts WashU DataHub JSON to UCSC TrackDb Textfile')
    parser.add_argument('-i', '--input', help='Input JSON file')
    parser.add_argument('-o', '--output', help='Output Text file')
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    output = process_tracks(data)
    with open(args.output, 'w') as f:
        f.write(output)
