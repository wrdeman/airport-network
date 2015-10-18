from collections import OrderedDict

from flask import url_for


class BaseAirPlot(object):
    width = 900
    height = 560
    padding = {"top": 25, "left": 0, "right": 0, "bottom": 0}

    def get_json(self, **kwargs):
        spec = OrderedDict()

        spec['width'] = self.width
        spec['height'] = self.height
        spec['padding'] = self.padding

        spec['data'] = self.get_data(**kwargs)
        spec['scales'] = self.get_scales()
        spec['signals'] = self.get_signals()
        spec['marks'] = self.get_marks()
        spec['axes'] = self.get_axes()

        response = OrderedDict({
            "spec": spec
        })

        return response

    def get_data(self):
        raise NotImplementedError

    def get_scales(self):
        return []

    def get_signals(self):
        return []

    def get_marks(self):
        return []

    def get_axes(self):
        return []


class Histogram(BaseAirPlot):
    width = 450
    height = 280

    def get_data(self, **kwargs):
        return [
            {
                "name": "degrees",
                "url": url_for("degree"),
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "histogram"
                }
            }
        ]

    def get_scales(self):
        return [
            {
                "name": "xscale",
                "type": "ordinal",
                "range": "width",
                "domain": {
                    "data": "degrees",
                    "field": "category"
                }
            },
            {
                "name": "yscale",
                "range": "height",
                "nice": True,
                "domain": {
                    "data": "degrees",
                    "field": "amount"
                }
            }
        ]

    def get_axes(self):
        return [
            {"type": "x", "scale": "xscale"},
            {"type": "y", "scale": "yscale"}
        ]

    def get_marks(self):
        return [
            {
                "type": "rect",
                "from": {"data": "degrees"},
                "properties": {
                    "enter": {
                        "x": {
                            "scale": "xscale",
                            "field": "category"
                        },
                        "width": {
                            "scale": "xscale",
                            "band": True,
                            "offset": -1
                        },
                        "y": {
                            "scale": "yscale",
                            "field": "amount"
                        },
                        "y2": {
                            "scale": "yscale",
                            "value": 0
                        }
                    },
                    "update": {"fill": {"value": "steelblue"}},
                    "hover": {"fill": {"value": "red"}}
                }
            }
        ]


class BareMap(BaseAirPlot):
    def get_data(self, **kwargs):
        src = kwargs['src']
        dst = kwargs['dst']

        flight_url = url_for("flights")
        routes_url = flight_url
        if src and dst:
            routes_url = flight_url + '/' + src + '/' + dst
        return [
            {
                "name": "states",
                "url": "static/airports/us-10m.json",
                "format": {"type": "topojson", "feature": "states"},
                "transform": [
                    {
                        "type": "geopath", "projection": "albersUsa",
                        "scale": 1200, "translate": [450, 280]
                    }
                ]
            },
            {
                "name": "traffic",
                "url": flight_url,
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "flight_data"
                },
                "transform": [
                    {
                        "type": "aggregate", "groupby": ["origin"],
                        "summarize": [
                            {
                                "field": "count",
                                "ops": ["sum"],
                                "as": ["flights"]
                            }
                        ]
                    }
                ]
            },
            {
                "name": "airports",
                "url": url_for("airports"),
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "airport_data"
                },
                "transform": [
                    {
                        "type": "lookup", "on": "traffic", "onKey": "origin",
                        "keys": ["code"], "as": ["traffic"]
                    },
                    {
                        "type": "filter",
                        "test": "datum.traffic != null"
                    },
                    {
                        "type": "geo", "projection": "albersUsa",
                        "scale": 1200, "translate": [450, 280],
                        "lon": "longitude", "lat": "latitude"
                    },
                    {
                        "type": "filter",
                        "test": "datum.layout_x != null && datum.layout_y != null"
                    },
                    {"type": "sort", "by": "-traffic.flights"}
                ]
            },
            {
                "name": "routes",
                "url": routes_url,
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "flight_data"
                },
                "transform": [
                    #{ "type": "filter", "test": "hover && hover.code == datum.origin" },
                    {
                        "type": "lookup",
                        "on": "airports",
                        "onKey": "code",
                        "keys": ["origin", "destination"],
                        "as": ["_source", "_target"]
                    },
                    {
                        "type": "filter",
                        "test": "datum._source && datum._target"
                    },
                    {
                        "type": "linkpath",
                        "shape": "line"
                    }
                ]
            }
        ]

    def get_marks(self):
        return [
            {
                "type": "path",
                "from": {"data": "states"},
                "properties": {
                    "enter": {
                        "path": {"field": "layout_path"},
                        "fill": {"value": "#dedede"},
                        "stroke": {"value": "white"}
                    }
                }
            },
            {
                "type": "symbol",
                "from": {"data": "airports"},
                "properties": {
                    "enter": {
                        "x": {"field": "layout_x"},
                        "y": {"field": "layout_y"},
                        "size": {"scale": "size", "field": "traffic.flights"},
                        "fill": {"value": "steelblue"},
                        "fillOpacity": {"value": 0.8},
                        "stroke": {"value": "white"},
                        "strokeWidth": {"value": 1.5}
                    }
                }
            },
            {
                "type": "text",
                "interactive": False,
                "properties": {
                    "enter": {
                        "x": {"value": 895},
                        "y": {"value": 0},
                        "fill": {"value": "black"},
                        "fontSize": {"value": 20},
                        "align": {"value": "right"}
                    },
                    "update": {
                        "text": {"signal": "title"}
                    }
                }
            },
            {
                "type": "path",
                "interactive": False,
                "from": {"data": "routes"},
                "properties": {
                    "enter": {
                        "path": {"field": "layout_path"},
                        "stroke": {"value": "black"},
                        "strokeOpacity": {"value": 0.15}
                    }
                }
            }
        ]

    def get_scales(self):
        return [
            {
                "name": "size",
                "type": "linear",
                "domain": {"data": "traffic", "field": "flights"},
                "range": [16, 1000]
            }
        ]

    def get_signals(self):
        return [
            {
                "name": "hover", "init": None,
                "streams": [
                    {"type": "symbol:mouseover", "expr": "datum"},
                    {"type": "symbol:mouseout", "expr": "null"}
                ]
            },
            {
                "name": "title", "init": "U.S. Airports, 2008",
                "streams": [{
                    "type": "hover",
                    "expr": "hover ? hover.name + ' (' + hover.code + ')' : 'U.S. Airports, 2008'"
                }]
            }
        ]
