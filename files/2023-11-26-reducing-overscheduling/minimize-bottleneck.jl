using CSV
using DataFrames
using Gadfly
using SCIP
using JuMP

df = CSV.File("membership.csv") |> DataFrame
m = Model(SCIP.Optimizer)

individuals = sort(unique(df.individual))
teams = sort(unique(df.team))
slots = ["s1", "s2", "s3"]

# x[t,s] = 1 if team t meets during time slot s.
@variable(m, x[teams, slots], Bin)

# c[i,s] = number of overbookings for individual i during time slot s.
@variable(m, c[individuals, slots] >= 0)

# b = maximum numbers of overbookings.
@variable(m, b >= 0)

# Maximize the maximum number of overbookings.
@objective(m, Min, b)

# Each team meets exactly once.
for t in teams
    @constraint(m, sum(x[t, s] for s in slots) == 1)
end

# Individuals can attend at most one team meeting per time slot.
for g in groupby(df, :individual)
    i = first(g.individual)
    for s in slots
        @constraint(m, c[i, s] >= sum(x[t, s] for t in g.team) - 1)

        # b is the maximum number of overbookings.
        @constraint(m, b >= c[i, s])
    end
end

optimize!(m)

# Constrain the overbooking bottleneck.
bv = value(b)
@constraint(m, b <= bv)

# Minimize the sum of overbookings.
@objective(m, Min, sum(c))
optimize!(m)

xv = value.(x)
cv = value.(c[filter(n -> startswith(n, "mgr"), c.axes[1]), :])

println("Team schedules:")
println(xv)
println()

println("Individual overbookings:")
println(cv)
println()


# Convert output to data frames for plotting.
teamdf = DataFrame(
    team = String[],
    slot = String[],
    scheduled = Bool[]
)

for (t, s) in Iterators.product(xv.axes[1], xv.axes[2])
    push!(teamdf, [t, s, Bool(xv[t, s] > 0.5)])
end

overbookingdf = DataFrame(
    individual = String[],
    slot = String[],
    overbooking = Int[]
)

for (i, s) in Iterators.product(cv.axes[1], cv.axes[2])
    push!(overbookingdf, [i, s, Int(round(cv[i, s]))])
end

# Create SVGs.
plot(
    teamdf,
    x = :team,
    y = :slot,
    color = :scheduled,
    Geom.rectbin,
    Scale.color_continuous,
    Theme(alphas=[0.5])
) |> SVG("minimize-bottleneck-teams.svg", 8inch, 4inch)

plot(
    overbookingdf,
    x = :individual,
    y = :slot,
    color = :overbooking,
    Geom.rectbin,
    Scale.color_continuous,
    Theme(alphas=[0.5])
) |> SVG("minimize-bottleneck-managers.svg", 8inch, 4inch)
