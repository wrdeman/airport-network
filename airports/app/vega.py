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
        spec['predicates'] = self.get_predicates()
        spec['marks'] = self.get_marks()
        spec['axes'] = self.get_axes()

        response = OrderedDict({
            "spec": spec,
            "renderer": 'svg'
        })

        return response

    def get_data(self):
        raise NotImplementedError

    def get_scales(self):
        return []

    def get_predicates(self):
        return []

    def get_signals(self):
        return []

    def get_marks(self):
        return []

    def get_axes(self):
        return []


class Scatter(BaseAirPlot):
    width = 600
    height = 480
    padding = {"top": 0, "left": 25, "right": 0, "bottom": 25}

    def get_data(self, **kwargs):
        return [
            {
                "name": "points",
                "url": url_for(
                    "degree",
                    plot_type='scatter',
                    network=kwargs['network']
                ),
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "scatter_points"
                },
            },
            {
                "name": "bestfit",
                "url": url_for(
                    "degree",
                    plot_type='powerlaw',
                    network=kwargs['network']
                ),
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "bestfit"
                },
            }
        ]

    def get_scales(self):
        return [
            {
                "name": "x",
                "nice": True,
                "type": "log",
                "range": "width",
                "domain": {"data": "points", "field": "x"}
            },
            {
                "name": "y",
                "nice": True,
                "type": "log",
                "range": "height",
                "domain": {"data": "points", "field": "y"}
            }
        ]

    def get_axes(self):
        return [
            {"type": "x", "scale": "x"},
            {"type": "y", "scale": "y"}
        ]

    def get_marks(self):
        return [
            {
                "type": "symbol",
                "from": {"data": "points"},
                "properties": {
                    "enter": {
                        "x": {
                            "scale": "x",
                            "field": "x"
                        },
                        "y": {
                            "scale": "y",
                            "field": "y"
                        },
                        "stroke": {"value": "steelblue"},
                        "fillOpacity": {"value": 0.5}
                    },
                    "update": {
                        "fill": {"value": "transparent"},
                        "size": {"value": 100}
                    },
                    "hover": {
                        "fill": {"value": "pink"},
                        "size": {"value": 300}
                    }
                }
            },
            {
                "type": "line",
                "from": {"data": "bestfit"},
                "properties": {
                    "enter": {
                        "x": {
                            "scale": "x",
                            "field": "x"
                        },
                        "y": {
                            "scale": "y",
                            "field": "y"
                        },
                        "stroke": {"value": "steelblue"},
                        "fillOpacity": {"value": 0.5}
                    },
                    "update": {
                        "fill": {"value": "transparent"},
                        "size": {"value": 100}
                    },
                    "hover": {
                        "fill": {"value": "pink"},
                        "size": {"value": 300}
                    }
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
            routes_url = url_for(
                "flights",
                departure_code=src,
                destination_code=dst
            )
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
            },
            {
                "type": "text",
                "properties": {
                    "enter": {
                        "align": {"value": "center"},
                        "fill": {"value": "#000"},
                    },
                    "update": {
                        "x": {
                            "signal": "tooltip.layout_x",
                            "offset": 25
                        },
                        "y": {
                            "signal": "tooltip.layout_y",
                            "offset": -10
                        },
                        "text": {"signal": "tooltip.name"},
                        "fillOpacity": {
                            "rule": [
                                {
                                    "predicate": {
                                        "name": "ifTooltip",
                                        "id": {"value": None}
                                    },
                                    "value": 0
                                },
                                {"value": 1}
                            ]
                        }
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
            },
            {
                "name": "xscale",
                "range": "width",
                "domain": {
                    "data": "airports", "field": "layout_x"
                }
            },
            {
                "name": "yscale",
                "range": "height",
                "domain": {
                    "data": "airports", "field": "layout_y"
                }
            }

        ]

    def get_signals(self):
        return [
            {
                "name": "tooltip",
                "init": {},
                "streams": [
                    {"type": "symbol:mouseover", "expr": "datum"},
                    {"type": "symbol:mouseout", "expr": "{}"}
                ]
            }
        ]

    def get_predicates(self):
        return [
            {
                "name": "ifTooltip",
                "type": "==",
                "operands": [
                    {"signal": "tooltip._id"},
                    {"arg": "id"}
                ]
            }
        ]


class LondonMap(BaseAirPlot):
    def get_data(self, **kwargs):
        scaling = 41000
        trans_x = 480
        trans_y = 43350

        line = kwargs['line']

        line_url = url_for("lines")
        if line:
            line_url = url_for(
                "lines",
                line=line
            )

        return [
            {
                "name": "boroughs",
                "url": "static/airports/london_boroughs.json",
                "format": {"type": "topojson", "feature": "london"},
                "transform": [
                    {
                        "type": "geopath", "projection": "mercator",
                        "scale": scaling, "translate": [trans_x, trans_y]
                    }
                ]
            },
            {
                "name": "stations",
                "url": url_for("stations"),
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "stations"
                },
                "transform": [
                    {
                        "type": "geo", "projection": "mercator",
                        "scale": scaling, "translate": [trans_x, trans_y],
                        "lon": "longitude", "lat": "latitude"
                    },
                    {
                        "type": "filter",
                        "test": "datum.layout_x != null && datum.layout_y != null"
                    },
                ]
            },
            {
                "name": "lines",
                "url": line_url,
                "format": {
                    "type": "json",
                    "parse": "auto",
                    "property": "lines"
                },
                "transform": [
                    {
                        "type": "lookup",
                        "on": "stations",
                        "onKey": "name",
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
                "from": {"data": "boroughs"},
                "properties": {
                    "enter": {
                        "path": {"field": "layout_path"},
                        "fill": {"value": "#43484A"},
                        "stroke": {"value": "white"}
                    }
                }
            },
            {
                "type": "symbol",
                "from": {"data": "stations"},
                "properties": {
                    "enter": {
                        "x": {"field": "layout_x"},
                        "y": {"field": "layout_y"},
                        "size": {"value": 5},
                        "fill": {"value": "steelblue"},
                        "fillOpacity": {"value": 0.8},
                        "stroke": {"value": "black"},
                        "strokeWidth": {"value": 1.5}
                    }
                }
            },
            {
                "type": "path",
                "interactive": False,
                "from": {"data": "lines"},
                "properties": {
                    "enter": {
                        "path": {"field": "layout_path"},
                        "stroke": {"scale": "color", "field": "line"},
                        "strokeOpacity": {"value": 0.5},
                        "strokeWidth": {"value": 4}
                    }
                }
            },
            {
                "type": "text",
                "properties": {
                    "enter": {
                        "align": {"value": "center"},
                        "fill": {"value": "#000"},
                    },
                    "update": {
                        "x": {
                            "signal": "tooltip.layout_x",
                            "offset": 25
                        },
                        "y": {
                            "signal": "tooltip.layout_y",
                            "offset": -10
                        },
                        "text": {"signal": "tooltip.name"},
                        "fillOpacity": {
                            "rule": [
                                {
                                    "predicate": {
                                        "name": "ifTooltip",
                                        "id": {"value": None}
                                    },
                                    "value": 0
                                },
                                {"value": 1}
                            ]
                        }
                    }
                }
            }
        ]

    def get_scales(self):
        return [
            {
                "name": "color",
                "type": "ordinal",
                "domain": {"data": "lines", "field": "line"},
                "range": "category10"
            },
            {
                "name": "xscale",
                "range": "width",
                "domain": {
                    "data": "stations", "field": "layout_x"
                }
            },
            {
                "name": "yscale",
                "range": "height",
                "domain": {
                    "data": "stations", "field": "layout_y"
                }
            }
        ]

    def get_signals(self):
        return [
            {
                "name": "tooltip",
                "init": {},
                "streams": [
                    {"type": "symbol:mouseover", "expr": "datum"},
                    {"type": "symbol:mouseout", "expr": "{}"}
                ]
            }
        ]

    def get_predicates(self):
        return [
            {
                "name": "ifTooltip",
                "type": "==",
                "operands": [
                    {"signal": "tooltip._id"},
                    {"arg": "id"}
                ]
            }
        ]
