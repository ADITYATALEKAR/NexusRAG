"""Steps for the routed query flow."""

from __future__ import annotations

from src.layer3_flows.routed_query_flow.states import RoutedQueryContext, RoutedQueryState


class SecurityCheckStep:
    """Run pre-routing security validation."""

    async def execute(self, flow: "RoutedQueryFlow", context: RoutedQueryContext) -> bool:
        """Return whether execution may proceed."""
        blocked_answer = flow._run_security_checks(context.query)
        if blocked_answer is None:
            return True
        context.answer = blocked_answer
        context.state = RoutedQueryState.FILTERED
        return False


class RouteDecisionStep:
    """Compute or override the routing decision."""

    async def execute(self, flow: "RoutedQueryFlow", context: RoutedQueryContext) -> None:
        """Populate the routing decision on the context."""
        context.state = RoutedQueryState.ROUTING
        context.routing_decision = flow._build_routing_decision(context.query, context.forced_route)


class RouteExecutionStep:
    """Execute the selected route and build diagnostics."""

    async def execute(self, flow: "RoutedQueryFlow", context: RoutedQueryContext) -> None:
        """Execute the selected route using the flow implementation."""
        if context.routing_decision is None:
            raise ValueError("Routing decision must exist before route execution")
        context.state = RoutedQueryState.EXECUTING
        answer, diagnostics = await flow._execute_routed(context.query, context.routing_decision)
        context.answer = answer
        context.diagnostics = diagnostics
        context.state = RoutedQueryState.COMPLETED if diagnostics is not None else RoutedQueryState.FILTERED
