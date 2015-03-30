//Global functions
window.onerror = function (msg, url, line) {
    alert("Message : " + msg + "\nURL : " + url + "\nLine number : " + line );
}

function OpenInNewTab(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

var quarkLib = (function quarkLib() {

    // Return the constructor
    return function quarkLibConstructor() {
        var _this = this; 

        var loff = 100;
        var roff = 50;
	var toff = 90;
        var boff = 90;
	var w = 600;
	var h = 200;
	var axisPadding = 30;
	var dataColor = "#5581b8";  //"mid blue" from minilims css
        var selectedColor = "darkseagreen";

        //Barplot with x and y axis.
        _this.seqBarPlot = function (id,plotObj) {

	    var chart = d3.select(id)
	      .append("svg")
	        .attr("class", "chart")
	        .attr("width", w + loff + roff)
	        .attr("height", h + toff + boff)
              .append("g")
	        .attr("transform", "translate(" + loff + "," + toff + ")");

	    var y = d3.scale.linear()
	    .domain([0, Math.max.apply(Math, plotObj.data)])
	    .range([h, 0]);
    
	    var x = d3.scale.ordinal()
            .domain(d3.range(plotObj.data.length))
	    .rangeBands([0, w]);

	    var bars = chart.selectAll("rect").data(plotObj.data);
    
	    bars.enter().append("rect")
	    .classed("bars", true)
	    .attr("x", function(d, i) { return i * x.rangeBand() + 1; })
	    .attr("width", x.rangeBand() - 1) 
            .attr("y", function(d) { return y(d); })
	    .attr("height", function(d) { return h-y(d); })
	    .attr("fill", dataColor);

	    var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .ticks(5);

	    chart.append("g")
	    .attr("class", "axis")
	    .call(yAxis); 

	    var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom")

	    //set up x-axis tick marks
	    if (plotObj.data.length > 20) {  //reduce number of tick labels shown if number of points is large
		pointsPerTick = Math.floor(plotObj.data.length/10);
		tickVals = [0];
		while( d3.max(tickVals) < d3.max(x.domain())-pointsPerTick ) {
		    last = tickVals[tickVals.length-1]; 
		    tickVals.push(last+pointsPerTick);
		}
		xAxis.tickValues(tickVals)
	    } else {
		xAxis.ticks(10)
	    }
	    xAxis.tickFormat(function(d) { return plotObj.dates[d]; }); 

	    chart.append("g")
	    .attr("class", "axis")
	    .attr("transform", "translate(0," + h + ")")
	    .call(xAxis)
	    .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-1em")
            .attr("dy", "-.5em")
	    .attr("transform", function(d) {
                return "rotate(-90)"});

	    chart.append("text")
	    .attr("x", (w / 2))             
	    .attr("y", -40)
	    .attr("text-anchor", "middle")  
	    .style("font-size", "16px") 
	    .text(plotObj.plot_title);

            var bars = chart.selectAll("rect.bars");
	    bars.append("title").text(function(d,i) {return plotObj.names[i];});
            bars.on("mouseover", function() {  
                    d3.select(this)
                    .attr("fill", selectedColor);})
                .on("mouseout", function() {  
                    d3.select(this)
                    .attr("fill", dataColor);})
                .on("click", function(d,i) {
 	            OpenInNewTab("/seqstats/showrorl?rorl=" + plotObj.names[i])});
	    //for debugging:  var bars = d3.select("#mychart").select("svg.chart").selectAll("rect.bars")
	};

        //Histogram plot for minilims
        _this.minilimsHistogram = function (id,plotObj,selectedNames,data_type) {

	    console.log("selectedNames:");
	    console.log(selectedNames);

	    console.log("plotObj.data:");
	    console.log(plotObj.data);

	    //find data for selected items
	    var svals = []; 
	    if (!$.isArray(selectedNames)) selectedNames = Array(selectedNames);
	    for(var i=0; i < plotObj.data.length; i++){
		if ($.inArray(plotObj.names[i], selectedNames) > -1)  {
		    svals.push(plotObj.data[i]);
		}
	    }

	    var x = d3.scale.linear()
	    .domain([0, d3.max(plotObj.data)])
	    .range([0, w]);

	    var hdata = d3.layout.histogram()
	    .bins(x.ticks(20))(plotObj.data);

            var run_bin; //find bins to which svals belong
	    var sbins = Array(svals.length+1).join('.').split(''); //initial dummy value for bin
	    for(run_bin = 0; run_bin < hdata.length; run_bin++) {  
		for(var i=0; i < svals.length; i++) {
		    if ( (svals[i] < hdata[run_bin].x + hdata[run_bin].dx) && (sbins[i] == ".") ) { 
			sbins[i] = run_bin; 
		    }
		}
	    }

            var y = d3.scale.linear()
	    .domain([0, d3.max(hdata, function(d) { return +d.y; })])
            .range([h, 0]);

	    var chart = d3.select(id)
	      .append("svg")
	        .attr("class", "chart")
	        .attr("width", w + loff + roff)
	        .attr("height", h + toff + boff)
              .append("g")
	        .attr("transform", "translate(" + loff + "," + toff + ")");

	    var bar = chart.selectAll("rect")
	        .data(hdata).enter()
              .append("rect")
                .classed("bars", true)
                .attr("x", function(d) { return x(d.x); })
                .attr("width", x(hdata[0].dx))
                .attr("y", function(d) { return y(d.y); })
                .attr("height", function(d) { return h-y(d.y); })
	        .attr("fill", function(d,i) { 
		    if ($.inArray(i,sbins) > -1) { 
			return selectedColor; 
		    } else { 
			return dataColor; 
		    }});
	    bar.append("title").text(function(d,i) {return plotObj.names[i];});


	    var yAxis = d3.svg.axis()
    	        .scale(y)
	        .orient("left")
	        .ticks(5);

	    chart.append("g")
	        .attr("class", "axis")
	        .call(yAxis); 

	    var xAxis = d3.svg.axis()
	        .scale(x)
	        .orient("bottom")
	        .tickFormat(function(d) { 
		    if (data_type == "Cluster Density") { 
			return d/1000; 
		    } else {
			return d;
		    }});

	    chart.append("g")
	        .attr("class", "axis")
	        .attr("transform", "translate(0," + h + ")")
   	        .call(xAxis); 

            chart.append("text")  //x-axis label
                .attr("x", (w / 2))
                .attr("y", h + 38)
                .attr("text-anchor", "middle")
                .style("font-size", "13px")
  	        .text(function() {
		    if (data_type == "Cluster Density") { 
			return "Cluster Denisty (Thousands per square millimeter)";
		    } else if (data_type == "Percent") { 
			return "Percent";
		    } else { 
			return "";
		    }});
	    
            chart.append("text")  //y-axis label
	        .attr("transform", "rotate(-90)")
                .attr("x", -h/2)
                .attr("y", -30)
                .attr("text-anchor", "middle")
                .style("font-size", "12px")
                .text("Number of " + plotObj.RorL + "s at Bauer Core");  //plotObj.RorL is "run" or "lane"
	    
            chart.append("text")  //plot title
                .attr("x", (w / 2))
                .attr("y", -60)
                .attr("text-anchor", "middle")
                .style("font-size", "16px")
                .text(plotObj.plot_title);

	    if (typeof(plotObj.subtitles) !== 'undefined') {
		for(var i=0; i < plotObj.subtitles.length; i++) {
		    chart.append("text")  //plot subtitle
			.attr("x", (w / 2))
			.attr("y", -40 + 15*i)
			.attr("text-anchor", "middle")
			.style("font-size", "12px")
			.text(plotObj.subtitles[i]);
		}
	    }
	    return(chart);
	};


        //Histogram plot for minilims, but with clickable points, and no highlighting
        _this.seqHistogram = function (id,plotObj,data_type) {
	    var chart =_this.minilimsHistogram(id,plotObj,data_type);

            var bars = chart.selectAll("rect");
            bars.on("mouseover", function() {  
                    d3.select(this)
                    .attr("fill", selectedColor);})
                .on("mouseout", function() {  
                    d3.select(this)
                    .attr("fill", dataColor);})
                .on("click", function(d,i) {
 	            OpenInNewTab("/seqstats/showrorl?rorl=" + plotObj.names[i])});

	};

	_this.scatterPlot = function (id,Xdata,Ydata) {
	    var chart = d3.select(id)
	      .append("svg")
	        .attr("class", "chart")
	        .attr("width", w + loff + roff)
	        .attr("height", h + toff + boff)
              .append("g")
	        .attr("transform", "translate(" + loff + "," + toff + ")");

	    var y = d3.scale.linear()
	    .domain([0, Math.max.apply(Math, Ydata)])
	    .range([h, 0]);
    
	    var x = d3.scale.linear()
	    .domain([0, Math.max.apply(Math, Xdata)])
	    .range([0, w]);

	    var dots = chart.selectAll("circle").data(Xdata).enter().append("circle");
            dots.attr("cx",function(d,i){ return x(d); });
            dots.attr("cy",function(d,i){ return y(Ydata[i]); });
            dots.attr("fill",dataColor)
                .attr("r",5)
                .style("stroke", "black")
	        .style("stroke-width", 1);

	    var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left")
	    .ticks(5);

	    chart.append("g")
	    .attr("class", "axis")
	    .call(yAxis); 

	    var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom")
	    .ticks(5);

	    chart.append("g")
	    .attr("class", "axis")
	    .attr("transform", "translate(0," + h + ")")
	    .call(xAxis); 

            return(chart);

	};

	_this.seqScatterPlot = function (id,plotObj) {
            console.log(plotObj.plot_title);
	    var chart = _this.scatterPlot(id,plotObj.x.data,plotObj.y.data);

	    chart.append("text")
	    .attr("x", (w / 2))             
	    .attr("y", -20)
	    .attr("text-anchor", "middle")  
	    .style("font-size", "14px") 
	    .text(plotObj.plot_title);

            var dots = chart.selectAll("circle");
	    dots.append("title").text(function(d,i) {return plotObj.x.names[i];});
            dots.on("mouseover", function() {  
                    d3.select(this)
                    .attr("fill", selectedColor);})
                .on("mouseout", function() {  
                    d3.select(this)
                    .attr("fill", dataColor);})
                .on("click", function(d,i) {
 	            OpenInNewTab("/seqstats/showrorl?rorl=" + plotObj.x.names[i])});
	};
    };
}());

