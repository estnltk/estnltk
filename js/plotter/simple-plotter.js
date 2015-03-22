/*
 * 
 * Selection frame inspired by Lars Gersmann's code at http://bl.ocks.org/lgersman/5311083
 * 
 */

function SimplePlotter (data,svg_id) {
    this.data = data;
    this.svg = d3.select("#"+svg_id);
    this.svg_id = svg_id;
    
    // Colour parameters
    this.colour = {
	term: 'black',
	selectedTerm: 'green',
	temporarySelectedTerm: 'red',
	concept: 'blue',
	selectedConcept: 'yellow'
    };
    
    // Numerical parameters
    this.num = {
	padding: 40, // Width of the "frame" from svg outer border to actual plot
	small_r: 5,
	large_r: 8
    };
    
    this.key = {
	aggregate: 13,
	expand: 46,
	rename: 8	
    };
    
    this.merge = function (class_label) {
	var new_circle;
	var simple_plotter = this;
	if(!simple_plotter.svg.selectAll("." + class_label).empty()) {
	    var total_x = 0;
	    var total_y = 0;
	    var N = 0;
	    var terms = [];
	    simple_plotter.svg.selectAll("." + class_label).each(function(circle_data,i) {
		total_x += circle_data.x;
		total_y += circle_data.y;
		N += 1;
		terms.push(this);
	    });

	    var avg_x = total_x/N;
	    var avg_y = total_y/N;
	    simple_plotter.svg.selectAll("." + class_label).attr("visibility","hidden").each(function(circle_data,i) {
		$(d3.select(this)[0]).data("label").attr("visibility","hidden");
	    });

	    d3.selectAll("circle."+class_label).classed(class_label,false).attr("fill",simple_plotter.colour.term);
	    
	    new_circle = simple_plotter.svg.append("circle")
		.attr("class","merged_circle selected")
		.attr("cx", x(avg_x))
		.attr("cy", y(avg_y))
		.attr("r",simple_plotter.num.large_r)
		.attr("fill",simple_plotter.colour.selectedConcept)
		.on("mousedown",function() {
		    if(!d3.selectAll('circle.selected').empty() && !d3.select(this).classed("selected") && !d3.selectAll('circle.selected').classed("merged_circle")) {

			var tmp = simple_plotter.svg.selectAll('circle.selected').classed("selection2",true).classed("selected",false);
			
			var selected = d3.select(this).classed("selected",true);
			terms = $(selected[0]).data("terms");
			simple_plotter.expandSelected();
			
			d3.selectAll(terms).classed("selection2",true);
			
			var merged_circle = simple_plotter.merge("selection2");
			merged_circle.classed("selected",true);
			
			//simple_plotter.renameMergedCircle();
			
			d3.event.stopPropagation();
			
		    } else if(d3.select(this).classed("selected")) {
			d3.select(this).classed("selected",false).attr("fill",simple_plotter.colour.concept);
			//d3.event.stopPropagation();
		    } else {
			d3.select(".selected").classed("selected",false).attr("fill",simple_plotter.colour.concept);
			d3.select(this).classed("selected",true).attr("fill",simple_plotter.colour.selectedConcept);
			
			//populate_concept_contents()
			//$("#concept_content").show(0);
			
			//var position = $(d3.select(this)[0]).position();
			//var x = position.x+20;
			//var y = position.y-20;
			
			//$("#concept_content").css("x",x).css("y",y);
			
			d3.event.stopPropagation();
		    }
		});
		
	    $(new_circle[0]).data("terms",terms);
	    simple_plotter.renameMergedCircle();
	}
	return new_circle;
    };
    
    this.drawPlot = function() {
	var simple_plotter = this;
	
	var data = this.data;

	this.svg.selectAll("*").remove();

	var svg_dim = document.getElementById(this.svg_id).getBoundingClientRect();
	var width = svg_dim.width;
	var height = svg_dim.height;
	
	x = d3.scale.linear().domain(d3.extent(data, function(d) {return d.x;})).range([this.num.padding,width-this.num.padding]);
	y = d3.scale.linear().domain(d3.extent(data, function(d) {return d.y;})).range([this.num.padding,height-this.num.padding]);

	this.svg.selectAll("circle")
	    .data(data)
	    .enter()
	    .append("circle")
	    .attr("class","circle")
	    .attr("cx", function(d) { return x(d.x); })
	    .attr("cy", function(d) { return y(d.y); })
	    .attr("r",simple_plotter.num.small_r)
	    .text(function(d) { return d.label; })//;
	    .on("click", function(d) {
		d3.selectAll('circle.selected').attr("fill",simple_plotter.colour.term).classed("selected", false);
		d3.select(this).attr("fill",simple_plotter.colour.selectedTerm).classed("selected",true);
	    })
	    .each(function(circle_data,i) {
		var parent_circle = d3.select(this);
		
		simple_plotter.addLabel(parent_circle,x(circle_data.x)+3,y(circle_data.y)-10,circle_data.label);
	    });
	    
	simple_plotter.svg
	    .on( "mousedown", function() {
		//$("#concept_content").hide(0);
		if (d3.event.defaultPrevented) return;
		d3.selectAll('circle.selected').attr("fill",simple_plotter.colour.term);
		d3.selectAll('.merged_circle').attr("fill",simple_plotter.colour.concept);
		//d3.selectAll('.merged_circle.selected').attr("fill",simple_plotter.colour.selectedConcept);
		
		d3.selectAll('circle.selected').classed("selected", false);

		var p = d3.mouse(this);

		simple_plotter.svg.append("rect")
		.attr({
		    rx      : 6,
		    ry      : 6,
		    class   : "selection",
		    x       : p[0],
		    y       : p[1],
		    width   : 0,
		    height  : 0
		})
		.style("stroke","gray")
		.style("stroke-dasharray","4px")
		.style("stroke-opacity","0.5")
		.style("fill","transparent");
		
	    })
	    .on( "mousemove", function() {
		var s = simple_plotter.svg.select( "rect.selection");

		if( !s.empty()) {
		    var p = d3.mouse(this),
			d = {
			    x       : parseInt( s.attr( "x"), 10),
			    y       : parseInt( s.attr( "y"), 10),
			    width   : parseInt( s.attr( "width"), 10),
			    height  : parseInt( s.attr( "height"), 10)
			},
			move = {
			    x : p[0] - d.x,
			    y : p[1] - d.y
			}
		    ;

		    if(move.x > 0) {
			d.width = move.x;
		    }
		    if(move.y > 0) {
			d.height = move.y;
		    }
		    s.attr( d);

		    d3.selectAll('.selected').classed( "selected", false);

		    d3.selectAll('.circle').each(function(circle_data, i) {
			circle_x = x(circle_data.x);
			circle_y = y(circle_data.y);
			if( 
			    !d3.select(this).classed("selected") && 
			    circle_x>=d.x && circle_x<=d.x+d.width && 
			    circle_y>=d.y && circle_y<=d.y+d.height
			) {
			    d3.select( this)
			    .classed("selection", true)
			    .classed("selected", true)
			    .attr("fill",simple_plotter.colour.temporarySelectedTerm);
			}
		    });
		}
	})
	.on( "mouseup", function() {
	    // remove selection frame
	    simple_plotter.svg.selectAll("rect.selection").remove();

	    // remove temporary selection marker class
	    d3.selectAll('.selection')
		.classed( "selection", false)
		.attr("fill",simple_plotter.colour.selectedTerm);
	})
	.on( "mouseout", function() {
	    if( d3.event.relatedTarget.tagName=='HTML') {
		    // remove selection frame
		simple_plotter.svg.selectAll( "rect.selection").remove();

		    // remove temporary selection marker class
		d3.selectAll( '.selection')
		    .attr("fill",simple_plotter.colour.term)
		    //.classed( "selection", false);
		d3.selectAll('.selected').attr("fill",simple_plotter.colour.selectedTerm);
	    }
	});
    };
    
    this.renameMergedCircle = function() {
	var new_label = prompt("New label:");
	
	var selected_circle = d3.select(".selected");
	if ($(selected_circle[0]).data("label") != undefined) $(selected_circle[0]).data("label").remove();
	
	$(selected_circle[0]).data("label",new_label);

	this.addLabel(selected_circle,parseInt(selected_circle.attr("cx"))+5,parseInt(selected_circle.attr("cy"))-18,new_label);
    };
    
    this.expandSelected = function () {
	var selected = this.svg.select(".selected");
	if (!selected.empty()) {
	    terms = $(selected[0]).data("terms");
	    d3.selectAll(terms).attr("visibility","visible").each(function(circle_data,i) {
		$(d3.select(this)[0]).data("label").attr("visibility","visible");
		//d3.select(this).classed("selected",true);
	    });
	    $(selected[0]).data("label").remove();
	    selected.remove();
	}
    };
    
    this.addLabel = function (d3_object,x,y,label) {
	this.svg.append("text")
		    .attr("x",x)
		    .attr("y",y)
		    .text(label)
		    // Disable text selection
		    .style("-moz-user-select","-moz-none")
		    .style("-khtml-user-select","none")
		    .style("-webkit-user-select","none")
		    .style("-ms-user-select","none")
		    .style("user-select","none")
		    .each(function(text_data,i) {
			$(d3_object[0]).data("label",d3.select(this));
		    });
    };
    
    this.export = function () {
	var circles = this.svg.selectAll("circle");
	
	var output = new Array();
	
	circles.each(function(circle_data,i) {
	    var circle = d3.select(this);
	    
	    if (circle.attr("visibility") == "hidden") return;
	    
	    var data = circle.data()[0];
	    
	    if (circle.classed("merged_circle")) {
		
		var parts = new Array();
		var raw_parts = $(circle[0]).data("terms");
		
		for (var j = 0; j < raw_parts.length; j++) {
		    raw_part = d3.select(raw_parts[j]).data()[0];
		    parts.push({label:raw_part.label,
				x: raw_part.x,
				y: raw_part.y
		    });
		}
		
		output.push({label:$(circle[0]).data("label").html(),parts:parts});
	    } else {
		output.push({label:data.label,
			    x:	data.x,
			    y:	data.y
		})
	    }
	});
	
	return output;
    }
    
    var simple_plotter = this;
    
    $(document).on("keydown", function(e) {
    switch(e.which) {
	case simple_plotter.key.aggregate:
	    simple_plotter.merge("selected");
	    break;
	case simple_plotter.key.expand:
	    simple_plotter.expandSelected();
	    break;
	case simple_plotter.key.rename:
	    simple_plotter.renameMergedCircle();
    }
});
    
}


