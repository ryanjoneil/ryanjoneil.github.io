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

# y[i,s] = 1 if individual i has a team meeting during time slot s.
@variable(m, y[individuals, slots], Bin)

# Maximize the number of meetings each individual can attend.
@objective(m, Max, sum(y))

# Each team meets exactly once.
for t in teams
    @constraint(m, sum(x[t, s] for s in slots) == 1)
end

# Individuals can attend at most one team meeting per time slot.
for g in groupby(df, :individual)
    i = first(g.individual)
    for s in slots
        @constraint(m, y[i, s] <= sum(x[t, s] for t in g.team))
    end
end

optimize!(m)
xv = value.(x)
yv = value.(y[filter(n -> startswith(n, "mgr"), y.axes[1]), :])

println("Team schedules:")
println(xv)
println()

println("Manager schedules:")
println(yv)
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

attendancedf = DataFrame(
    individual = String[],
    slot = String[],
    attendance = Bool[]
)

for (i, s) in Iterators.product(yv.axes[1], yv.axes[2])
    push!(attendancedf, [i, s, Bool(yv[i, s] > 0.5)])
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
) |> SVG("maximize-attendance-teams.svg", 8inch, 4inch)

plot(
    attendancedf,
    x = :individual,
    y = :slot,
    color = :attendance,
    Geom.rectbin,
    Scale.color_continuous,
    Theme(alphas=[0.5])
) |> SVG("maximize-attendance-managers.svg", 8inch, 4inch)
