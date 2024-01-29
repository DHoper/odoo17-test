/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo_list/todo_list";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

const serviceRegistry = registry.category("services");

export class Playground extends Component {
    constructor(env, services) {
        super();
        this.setup(env, services);
    }

    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList };

    setup(env, services) {
        this.str1 = "<div class='text-primary'>some content</div>";
        this.str2 = markup("<div class='text-primary'>some content</div>");
        this.sum = useState({ value: 2 });
        console.log(serviceRegistry, 989898);
        this.statistics = useState(useService("liveCCC"));
        this.orm = useService("orm");

        setInterval(() => {
            console.log("787887", this.statistics);
        }, 10000);
    }

    incrementSum() {
        this.sum.value++;
    }
}
