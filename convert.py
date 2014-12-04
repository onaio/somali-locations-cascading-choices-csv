import codecs
import unicodecsv as csv

from pyxform.xls2json_backends import xls_to_dict


class GenerateLocationCascade(object):
    def __init__(self, regions, villages):
        self._regions = {}
        self.regions = self._regions_to_dict(regions)
        self.villages = villages
        self.districts = {}
        self.ao = {}
        self._region_list = {}

    def _regions_to_dict(self, regions):
        result = {}
        for region in regions:
            name = region['Region']
            code = region['Region Code']
            result[name.lower()] = code
            self._regions[code] = {'name': name, 'code': code}

        return result

    def get_region_code(self, name):
        return self.regions[name.lower()]

    def _set_district_info(self, district, village, region, ao,
                           list_name='districts'):
        if not self.districts.get(district):
            name = village['District']
            self.districts[district] = (
                list_name, district, name, name, ao, region)

    def _set_region_info(self, region, village, ao, list_name='regions'):
        if not self._region_list.get(region):
            info = self._regions.get(region)
            name = info.get('name')
            self._region_list[region] = (list_name, region, name, name, ao)

    def _set_ao(self, village, list_name='ao'):
        ao = village['AO'].lower().replace(' ', '_')
        if not self.ao.get(ao):
            name = village['AO']
            self.ao[ao] = (list_name, ao, name, name)

    def _get_list_values(self, list_var):
        if not list_var:
            self.village_cascade()

        return list_var.values()

    def ao_cascade(self):
        return self._get_list_values(self.ao)

    def region_cascade(self):
        return self._get_list_values(self._region_list)

    def district_cascade(self):
        return self._get_list_values(self.districts)

    def village_cascade(self, list_name='villages'):
        data = []
        self.districts = {}

        for village in self.villages:
            village_code = village.get('Village Code') \
                or village.get('Village')
            village_label = village.get('Village')
            ao = village['AO'].lower().replace(' ', '_')
            district = village['District Code']

            region = village.get('Region')
            if region == 'L Juba':
                region = 'Lower Juba'
            region = self.get_region_code(region)
            data.append((
                list_name, village_code, village_label, village_label, ao,
                region, district))

            self._set_ao(village)
            self._set_region_info(region, village, ao)
            self._set_district_info(district, village, region, ao)

        return data

    def write_location_cascade_csv(self, filename='location.csv'):
        headers = ('list name', 'name', 'label:English', 'label:Somali',
                   'ao', 'region', 'district')
        with codecs.open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(self.ao_cascade())
            writer.writerows(self.region_cascade())
            writer.writerows(self.district_cascade())
            writer.writerows(self.village_cascade())


if __name__ == '__main__':
    path = 'data.xlsx'
    doc = xls_to_dict(path)
    vdb = doc['VDB']
    districts = doc['District Names']
    regions = doc['Region Name']

    g = GenerateLocationCascade(regions, vdb)
    g.write_location_cascade_csv()
