ace.define("ace/mode/jinja", ["require", "exports", "module", "ace/lib/oop", "ace/mode/html", "ace/mode/text_highlight_rules"], function(require, exports, module) {
    var oop = require("ace/lib/oop");
    var HtmlMode = require("ace/mode/html").Mode;
    var TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

    var JinjaHighlightRules = function() {
        this.$rules = {
            "start": [
                {
                    token: "variable",
                    regex: "{{",
                    next: "jinja-start"
                },
                {
                    token: "comment",
                    regex: "{#",
                    next: "jinja-comment"
                },
                {
                    token: "keyword",
                    regex: "{%",
                    next: "jinja-start"
                }
            ],
            "jinja-start": [
                {
                    token: "variable",
                    regex: "}}",
                    next: "start"
                },
                {
                    token: "keyword",
                    regex: "%}",
                    next: "start"
                },
                {
                    defaultToken: "variable"
                }
            ],
            "jinja-comment": [
                {
                    token: "comment",
                    regex: "#}",
                    next: "start"
                },
                {
                    defaultToken: "comment"
                }
            ]
        };
    };
    oop.inherits(JinjaHighlightRules, TextHighlightRules);

    var Mode = function() {
        HtmlMode.call(this);
        this.HighlightRules = JinjaHighlightRules;
    };
    oop.inherits(Mode, HtmlMode);

    (function() {
        this.$id = "ace/mode/jinja";
    }).call(Mode.prototype);

    exports.Mode = Mode;
});
