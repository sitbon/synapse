<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <title>Dress Data</title>
    <link href="/static/dress.css" rel="stylesheet" type="text/css">
    <link href="/static/minimalist.css">
    <script language="javascript" type="text/javascript" src="/static/jquery-2.1.1.min.js"></script>
    <script language="javascript" type="text/javascript" src="/static/jquery.flot.min.js"></script>
    <script language="javascript" type="text/javascript" src="/static/jquery.rs.slideshow.min.js"></script>
    <script language="javascript" type="text/javascript" src="/static/flowplayer.mini.js"></script>
    <!-- Bootstrap core CSS -->
    <link href="static/boostrap/css/bootstrap.min.css" rel="stylesheet">

    <script language="Javascript" type="text/javascript">
    $(function() {
        var maxPoints = 20;
        var proximityIndex = 0, attentionIndex = 0, heartrateIndex = 0, imageIndex = 0;
        var proximityArray = [[0,0]], attentionArray = [[0,0]], heartrateArray = [[0,0]];

        var videoIndex = 0;       
        var videoArray = [[0,0]];

        /*
         * Data describing plots on graph.
         */
        var attentionData = {
                data: attentionArray,
                lines: {
                    show: true,
                    fill: true,
                    fillColor: "rgba(196,195,195,0.2)"
                },
                label: "Attention Level"
        };
        /*var proximityData = {
                data: proximityArray,
                lines: {
                    show: true
                },
                label: "Proximity Level"
        };*/
        var heartrateData = {
                data: heartrateArray,
                lines: {
                    show: true
                },
                label: "Heart Rate"
        };

        var dressPlot = $.plot("#dressPlot", 
            [attentionData, heartrateData],
            {
                series: {
                    shadowSize: 0
                },
                yaxis: {
                    min: 0,
                    max: 170
                },
                xaxis: {
                    show: false,
                    min: 0,
                    max: 19
                },
                colors: ["#c4c3c3", "#8d67ac"]
        });

        /*
         * Retrievs next video to add to video playlist
         */
        function getVideoData() {
        }
 
        /*
         * Retrieve attention data from server through API. If successful, add data points
         * to the graph.
         */
        function getAttentionData() {
            var attentionAPI = "http://192.168.42.1/data/attention/" + attentionIndex;
            $.getJSON(attentionAPI)
            .done(function(data) {
                if (data.success == true) {
                    attentionIndex = data.data[data.data.length-1][0];

                    // Remove the beginning of the array to add new points.
                    attentionArray = attentionArray.concat(data.data);
                    if (attentionArray.length > maxPoints) {
                        attentionArray = attentionArray.slice(attentionArray.length-maxPoints);
                    }

                    for (var i = 0; i < attentionArray.length; ++i) {
                        attentionArray[i][0] = i;
                    }
                    attentionData["data"] = attentionArray;
                } else {
                    // We didn't receive data, interpolate this as being the same data point as seen
                    // previously, in an effort to keep things sync'ed.
                    attentionArray.push(attentionArray[attentionArray.length-1].slice()); // We do this because javascript is the worst language ever, and we need a copy, not a reference.
                    if (attentionArray.length > maxPoints) {
                        attentionArray = attentionArray.slice(attentionArray.length-maxPoints);
                    }

                    for (var i = 0; i < attentionArray.length; ++i) {
                        attentionArray[i][0] = i;
                    }
                    attentionData["data"] = attentionArray;
                    console.log(attentionData["data"]);
                }
                setTimeout(getAttentionData, 1000);
            });
        }

        /*
         * Retrieve proximity data from server through API. If successful, add data points
         * to the graph.
         */
        function getProximityData() {
            var proximityAPI = "http://192.168.42.1/data/proximity/" + proximityIndex;
            $.getJSON(proximityAPI)
            .done(function(data) {
                if (data.success == true) {
                    proximityIndex = data.data[data.data.length-1][0];
                    var currProximity = data.data[data.data.length-1][1];

                    $('.target').hide();
                    if (currProximity >= 450) { // public
                        $('#publicCicle').show();
                    } else if (currProximity >= 250) { // social
                        $('#socialCircle').show();
                    } else if (currProximity >= 100) { // personal
                        $('#personalCircle').show();
                    } else if (currProximity >= 22) { // intimate
                        $('#intimateCircle').show();
                    }
                    // no data so we don't show anything.
                } else {
                    // We didn't receive data, interpolate this as no one being in proximity.
                    $('.target').hide();
                }
                setTimeout(getProximityData, 1000);
            });
        }

        /*
         * Retrieve heart rate data from server through API. If successful, add data points
         * to the graph.
         */
        function getHeartrateData() {
            var heartrateAPI = "http://192.168.42.1/data/heartrate/" + heartrateIndex;
            $.getJSON(heartrateAPI)
            .done(function(data) {
                if (data.success == true) {
                    heartrateIndex = data.data[data.data.length-1][0];

                    heartrateArray = heartrateArray.concat(data.data);
                    if (heartrateArray.length > maxPoints) {
                        heartrateArray = heartrateArray.slice(heartrateArray.length-maxPoints);
                    }

                    for (var i = 0; i < heartrateArray.length; ++i) {
                        heartrateArray[i][0] = i;
                    }
                    heartrateData["data"] = heartrateArray;
                } else {
                    // We didn't receive data, interpolate this as being the same data point as seen
                    // previously, in an effort to keep things sync'ed.
                    heartrateArray.push(heartrateArray[heartrateArray.length-1].slice()); // We do this because javascript is the worst language ever, and we need a copy, not a reference.
                    if (heartrateArray.length > maxPoints) {
                        heartrateArray = heartrateArray.slice(heartrateArray.length-maxPoints);
                    }

                    for (var i = 0; i < heartrateArray.length; ++i) {
                        heartrateArray[i][0] = i;
                    }
                    heartrateData["data"] = heartrateArray;
                }
                setTimeout(getHeartrateData, 1000);
            });
        }

        /*
         * Draw the graph with newest data.
         */
        function updateGraph() {
            dressPlot.setData([attentionData, heartrateArray]);
            dressPlot.draw();
            setTimeout(updateGraph, 1000);
        }

        /*
         * Retrieve new picture data from the server through the API. If new pictures
         * are found, add them to the slideshow and remove old pictures.
         */
        function getNewPictures() {
            var imageAPI = "http://192.168.42.1/data/image/" + imageIndex;
            $.getJSON(imageAPI)
            .done(function (data) {
                if (data.success == true) {
                    imageIndex = data.data[data.data.length-1][0];

                    var slides = [];
                    for (var i = 0; i < data.data.length; ++i) {
                        var s = data.data[i][1].replace("\"", "'");
                        slides.push({url: s});
                    }
                    while ($('#slideshow').rsfSlideshow('totalSlides')+data.data.length > 5) {
                        $('#slideshow').rsfSlideshow('removeSlides', 0);
                    }

                    $('#slideshow').rsfSlideshow('addSlides', slides);
                }
                setTimeout(getNewPictures, 5000);
            });
        }

        // Start slideshow with no data.
        $('#slideshow').rsfSlideshow({slides: []});

        $('.target').hide();

        // Start data gathering
        setTimeout(getAttentionData, 1000);
        setTimeout(getHeartrateData, 1000);
        setTimeout(getProximityData, 1000);
        setTimeout(getNewPictures, 1500);
        setTimeout(updateGraph, 1500);
    });
    </script>
</head>

<body>

    <div class="plot-container">                                                                               
        <div id="dressPlot" class="plot-placeholder"></div>                                                    
    </div>    

    <img class="logo" src="/images/logo_anouk.png" width="100" height="120">  
    
    <img class="anouk" src="/images/anouk.png" width="260" height="260">

    <div id="intimateCircle" class="target">
        <img class="intimate" src="/images/intimate.png" width="260" height="260">
    </div>

    <div id="personalCircle" class="target">
        <img class="personal" src="/images/personal.png" width="260" height="260">
    </div>

    <div id="socialCircle" class="target">
        <img class="social" src="/images/social.png" width="260" height="260">
    </div>

    <div id="publicCicle" class="target">
        <img class="public" src="/images/public.png" width="260" height="260">
    </div>

    <div id="noneCircle">
        <img class="none" src="/images/none.png" width="260" height="260">
    </div>

     <div id="slideshow" class="rs-slideshow">
        <div class="slide-container">
        </div>
    </div>
</body>
</html>
