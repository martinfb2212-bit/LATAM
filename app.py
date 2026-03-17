def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    years_avail   = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(c for c in df["country"].dropna().unique() if c not in EXCLUDED_COUNTRIES)

    page_header("Commercial Intelligence",
                "Year-over-Year Performance  ·  Growth Analysis  ·  Market Focus")

    ci_tabs = st.tabs([
        "📊  Overview & YoY",
        "🎯  Country Targets",
        "👥  Customer Intelligence",
        "📅  Seasonality",
    ])

    # ── Shared filters ────────────────────────────────────────────────────────
    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]

    with st.expander("⚙  Filters & Scope", expanded=True):
        sc1, sc2 = st.columns([1, 2])
        with sc1:
            scope = st.radio("Scope", ["📅  Year-to-Date", "📆  Full Year"], key="ci_scope")
        use_ytd = "Year-to-Date" in scope
        with sc2:
            if use_ytd:
                info_strip(f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. Prior years capped at week {current_week}.", "#2D4A3E")
            else:
                info_strip("Comparing <strong>all weeks in the system</strong> per year — including future confirmed orders.", "#B8924A")

        fc1, fc2, fc3 = st.columns(3)
        default_years = years_avail[-3:] if len(years_avail) >= 3 else years_avail
        sel_years     = fc1.multiselect("Years", years_avail, default=default_years, key="ci_years")
        sel_customers = fc2.multiselect("Customers", all_customers, default=[], key="ci_customers", placeholder="All customers")
        sel_countries = fc3.multiselect("Countries", all_countries, default=[], key="ci_countries", placeholder="All countries")

    if not sel_years:
        st.warning("Select at least one year.")
        return

    dff = df[df["delivery_year"].isin(sel_years)].copy()
    dff = dff[~dff["country"].isin(EXCLUDED_COUNTRIES)]
    if sel_customers: dff = dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff = dff[dff["country"].isin(sel_countries)]
    if use_ytd:       dff = dff[dff["delivery_week"] <= current_week]

    if dff.empty:
        st.info("No data matches the selected filters.")
        return

    cur_year   = max(sel_years)
    prev_year  = cur_year - 1
    prev2_year = cur_year - 2
    cy, py, p2y = str(cur_year), str(prev_year), str(prev2_year)
    scope_lbl = f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df   = dff[dff["delivery_year"]==cur_year]
    prev_df  = dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df = dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — OVERVIEW & YOY
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[0]:
        section_label(f"Summary  ·  {scope_lbl}  ·  {cur_year} vs {prev_year}")

        cur_ship  = n_shipments(cur_df)
        prev_ship = n_shipments(prev_df)
        cur_fob   = safe_float(cur_df["total_price"].sum())
        prev_fob  = safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
        cur_units = safe_float(cur_df["total_quantity"].sum())
        prev_units= safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Shipments",        f"{cur_ship:,}",       delta=metric_delta_str(cur_ship,  prev_ship))
        k2.metric("FOB Value",        f"$ {cur_fob:,.0f}",   delta=metric_delta_str(cur_fob,   prev_fob))
        k3.metric("Units Shipped",    f"{int(cur_units):,}", delta=metric_delta_str(cur_units, prev_units))
        k4.metric("Active Customers", f"{cur_df['customer_name'].nunique():,}")

        divider()
        section_label(f"Weekly FOB Trend  ·  {scope_lbl}")
        weekly = dff.groupby(["delivery_year","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        weekly["Year"] = weekly["delivery_year"].astype(str)
        fig_trend = px.line(weekly, x="delivery_week", y="fob", color="Year",
                            labels={"delivery_week":"ISO Week","fob":"FOB (USD)"},
                            color_discrete_sequence=PALETTE, markers=True)
        fig_trend.update_traces(line_width=2.5, marker_size=5)
        fig_trend.update_yaxes(tickprefix="$ ")
        plotly_layout(fig_trend, height=320)
        st.plotly_chart(fig_trend, use_container_width=True)

        divider()
        section_label("FOB by Country  ·  3-Year Comparison")
        cy_grp = dff.groupby(["country","delivery_year"]).agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique")).reset_index()
        cy_grp["Year"]  = cy_grp["delivery_year"].astype(str)
        cy_grp["label"] = cy_grp["country"].apply(lambda c: f"{flag(c)} {c}")
        order = cy_grp[cy_grp["Year"]==cy].sort_values("fob", ascending=False)["country"].tolist()
        cy_grp["sort_key"] = cy_grp["country"].apply(lambda c: order.index(c) if c in order else 999)
        cy_grp = cy_grp.sort_values("sort_key")
        fig_cntry = px.bar(cy_grp, x="label", y="fob", color="Year", barmode="group",
                           labels={"label":"Country","fob":"FOB (USD)"},
                           color_discrete_sequence=PALETTE)
        fig_cntry.update_yaxes(tickprefix="$ ")
        fig_cntry.update_xaxes(tickangle=-35)
        plotly_layout(fig_cntry, height=360)
        st.plotly_chart(fig_cntry, use_container_width=True)

        divider()
        section_label(f"Country Status Table  ·  {scope_lbl}")
        piv_fob = cy_grp.pivot_table(index="country", columns="Year", values="fob",   aggfunc="sum").reset_index()
        piv_shp = cy_grp.pivot_table(index="country", columns="Year", values="ships", aggfunc="sum").reset_index()
        country_rows = []
        for c in piv_fob["country"].unique():
            c_fob  = safe_float(safe_pivot_val(piv_fob,"country",c,cy))
            p_fob  = safe_float(safe_pivot_val(piv_fob,"country",c,py))
            p2_fob = safe_float(safe_pivot_val(piv_fob,"country",c,p2y))
            c_shp  = safe_int(safe_pivot_val(piv_shp,"country",c,cy))
            p_shp  = safe_int(safe_pivot_val(piv_shp,"country",c,py))
            p2_shp = safe_int(safe_pivot_val(piv_shp,"country",c,p2y))
            chg_py = pct_change(c_fob,p_fob)
            chg_p2 = pct_change(c_fob,p2_fob)
            badge  = status_badge(chg_py,c_fob)
            country_rows.append({
                "Country":      f"{flag(c)} {c}",
                f"Ships {cy}":  c_shp,
                f"Ships {py}":  p_shp  or "—",
                f"Ships {p2y}": p2_shp or "—",
                f"FOB {cy}":    f"$ {c_fob:,.0f}",
                f"FOB {py}":    f"$ {p_fob:,.0f}"  if p_fob  else "—",
                f"FOB {p2y}":   f"$ {p2_fob:,.0f}" if p2_fob else "—",
                f"vs {py}":     f"{chg_py:+.1f}%"  if chg_py is not None else "—",
                f"vs {p2y}":    f"{chg_p2:+.1f}%"  if chg_p2 is not None else "—",
                "Status":       badge,
            })
        country_rows.sort(
            key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")),
            reverse=True)
        st.dataframe(pd.DataFrame(country_rows), use_container_width=True, hide_index=True)

        divider()
        section_label(f"Customer Performance by Country  ·  {scope_lbl}")
        info_strip("Each country panel shows every customer active in any selected year.", "#8C3D3D")
        ccy = dff.groupby(["country","customer_name","delivery_year"]).agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique"),
            units=("total_quantity","sum")).reset_index()
        top_cntry = (ccy[ccy["delivery_year"]==cur_year]
                     .groupby("country")["fob"].sum()
                     .sort_values(ascending=False).index.tolist())
        for country in top_cntry + [c for c in ccy["country"].unique() if c not in top_cntry]:
            cdf_c = ccy[ccy["country"]==country]
            if cdf_c.empty: continue
            tot_fob = safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
            tot_shp = safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())
            with st.expander(
                f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f}  ({scope_lbl} {cur_year})",
                expanded=False):
                piv_c_fob  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="fob",   aggfunc="sum").reset_index()
                piv_c_shp  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="ships", aggfunc="sum").reset_index()
                piv_c_unit = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="units", aggfunc="sum").reset_index()
                cust_rows = []
                for _, r in piv_c_fob.iterrows():
                    cname  = r["customer_name"]
                    cf     = safe_float(r.get(cur_year,   0))
                    pf     = safe_float(r.get(prev_year,  0))
                    p2f    = safe_float(r.get(prev2_year, 0))
                    cs     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, cur_year))
                    ps     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, prev_year))
                    cu     = safe_int(safe_pivot_val(piv_c_unit, "customer_name", cname, cur_year))
                    chg    = pct_change(cf, pf)
                    chg2   = pct_change(cf, p2f)
                    cbadge = status_badge(chg, cf)
                    cust_rows.append({
                        "Customer":     cname,
                        f"FOB {cy}":    f"$ {cf:,.0f}",
                        f"FOB {py}":    f"$ {pf:,.0f}"  if pf  else "—",
                        f"FOB {p2y}":   f"$ {p2f:,.0f}" if p2f else "—",
                        f"vs {py}":     f"{chg:+.1f}%"  if chg  is not None else "—",
                        f"vs {p2y}":    f"{chg2:+.1f}%" if chg2 is not None else "—",
                        f"Ships {cy}":  cs,
                        f"Ships {py}":  ps or "—",
                        f"Units {cy}":  f"{cu:,}",
                        "Status":       cbadge,
                    })
                cust_rows.sort(
                    key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")),
                    reverse=True)
                if cust_rows:
                    st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)
                    cdf_cur = cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob", ascending=False).head(12)
                    if not cdf_cur.empty:
                        fig_mini = px.bar(cdf_cur, x="customer_name", y="fob",
                                          labels={"customer_name":"","fob":"FOB (USD)"},
                                          color_discrete_sequence=["#8C3D3D"])
                        fig_mini.update_yaxes(tickprefix="$ ")
                        fig_mini.update_xaxes(tickangle=-30)
                        plotly_layout(fig_mini, height=200)
                        st.plotly_chart(fig_mini, use_container_width=True)

        divider()
        section_label("Growth Opportunity Focus")
        decline = [r for r in country_rows if any(k in r["Status"] for k in ["Declining","At risk","Lost"])]
        growing = [r for r in country_rows if any(k in r["Status"] for k in ["Growing","Strong"])]
        new_mkt = [r for r in country_rows if "New" in r["Status"]]
        g1,g2,g3 = st.columns(3)
        def focus_col(col, title, color, items):
            col.markdown(
                f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;'
                f'text-transform:uppercase;color:{color};margin-bottom:10px;padding-bottom:8px;'
                f'border-bottom:2px solid {color};">{title}</div>', unsafe_allow_html=True)
            if not items:
                col.markdown('<div style="font-family:Jost,sans-serif;font-size:.82rem;color:#7A7A7A;padding:6px 0;">None</div>', unsafe_allow_html=True)
            for r in items:
                chg = r.get(f"vs {py}","—")
                col.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:7px 0;'
                    f'border-bottom:1px solid #EDE9E3;">'
                    f'<span style="font-family:Jost,sans-serif;font-size:.82rem;color:#1A1A1A;">{r["Country"]}</span>'
                    f'<span style="font-family:Jost,sans-serif;font-size:.75rem;font-weight:500;color:{color};">{chg}</span>'
                    f'</div>', unsafe_allow_html=True)
        focus_col(g1,"Needs attention","#8C3D3D",decline)
        focus_col(g2,"Growing markets","#2D4A3E",growing)
        focus_col(g3,"New markets","#B8924A",new_mkt)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — COUNTRY TARGETS
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[1]:
        section_label(f"Country Growth Targets  ·  {cur_year}  ·  {scope_lbl}", "#8C3D3D")
        info_strip(
            f"Set a FOB growth target (%) per country for <strong>{cur_year}</strong>. "
            f"The dashboard calculates the required FOB, your current gap, and pace vs the {current_week}-week mark.",
            "#2D4A3E")

        # Build base data
        cntry_cur  = cur_df.groupby("country").agg(fob_cur=("total_price","sum"),  ships_cur=("shipment_id","nunique")).reset_index()
        cntry_prev = prev_df.groupby("country").agg(fob_prev=("total_price","sum")).reset_index() if not prev_df.empty else pd.DataFrame(columns=["country","fob_prev"])
        cntry_base = cntry_cur.merge(cntry_prev, on="country", how="outer").fillna(0)

        # Add countries that existed last year but have 0 this year
        if not prev_df.empty:
            prev_only = prev_df[~prev_df["country"].isin(cntry_base["country"])].groupby("country").agg(fob_prev=("total_price","sum")).reset_index()
            prev_only["fob_cur"] = 0.0
            prev_only["ships_cur"] = 0
            cntry_base = pd.concat([cntry_base, prev_only], ignore_index=True)

        active_countries = sorted(cntry_base[cntry_base["fob_cur"]>0]["country"].tolist())
        all_tgt_countries= sorted(cntry_base["country"].tolist())

        # ── Target input form ────────────────────────────────────────────────
        section_label("Set Targets per Country", "#2D4A3E")

        # Store targets in session state — pre-load 2026 defaults on first run
        tgt_key = f"country_targets_{cur_year}"
        if tgt_key not in st.session_state:
            if cur_year == 2026:
                st.session_state[tgt_key] = {
                    c: DEFAULT_TARGETS_2026.get(c, 0.0) for c in all_tgt_countries
                }
            else:
                st.session_state[tgt_key] = {c: 0.0 for c in all_tgt_countries}

        # Show pre-set targets banner for 2026
        if cur_year == 2026:
            set_countries = ", ".join(
                f"{flag(c)} {c} <strong>{v:+.0f}%</strong>"
                for c, v in DEFAULT_TARGETS_2026.items()
                if c in all_tgt_countries
            )
            info_strip(
                f"Pre-set 2026 targets (based on 2025 actuals): {set_countries}. "
                f"You can override any value below.",
                "#2D4A3E")

        with st.form("target_form"):
            st.markdown(
                '<div style="font-family:Jost,sans-serif;font-size:.78rem;color:#4A4A4A;'
                'margin-bottom:12px;">Enter a growth % target for each country. '
                'Leave at 0 to exclude from tracking.</div>',
                unsafe_allow_html=True)

            n_cols = 4
            country_chunks = [all_tgt_countries[i:i+n_cols] for i in range(0, len(all_tgt_countries), n_cols)]
            new_targets = {}
            for chunk in country_chunks:
                cols = st.columns(n_cols)
                for col, country in zip(cols, chunk):
                    prev_val = safe_float(
                        cntry_base[cntry_base["country"]==country]["fob_prev"].values[0]
                        if country in cntry_base["country"].values else 0)
                    default  = safe_float(st.session_state[tgt_key].get(country, 0.0))
                    is_preset = cur_year == 2026 and country in DEFAULT_TARGETS_2026
                    label = f"{flag(country)} {country}" + (" ✦" if is_preset else "") + f"\n(prev: $ {prev_val:,.0f})"
                    val = col.number_input(
                        label,
                        min_value=-100.0, max_value=500.0,
                        value=default, step=1.0,
                        key=f"tgt_{cur_year}_{country}")
                    new_targets[country] = val

            submitted = st.form_submit_button("Save Targets  →", use_container_width=False)
            if submitted:
                st.session_state[tgt_key] = new_targets
                st.success("Targets saved.")

        targets = st.session_state.get(tgt_key, {c: DEFAULT_TARGETS_2026.get(c, 0.0) if cur_year==2026 else 0.0 for c in all_tgt_countries})

        divider()
        section_label(f"Target Dashboard  ·  {cur_year}", "#8C3D3D")

        # Build results table
        tgt_rows = []
        for _, r in cntry_base.iterrows():
            c        = r["country"]
            fob_cur  = safe_float(r["fob_cur"])
            fob_prev = safe_float(r["fob_prev"])
            tgt_pct  = safe_float(targets.get(c, 0.0))
            if tgt_pct == 0 and fob_prev == 0:
                continue
            tgt_fob  = fob_prev * (1 + tgt_pct/100) if fob_prev > 0 else 0.0
            gap      = tgt_fob - fob_cur
            pct_done = (fob_cur / tgt_fob * 100) if tgt_fob > 0 else (100.0 if fob_cur > 0 else 0.0)
            # Expected pace: what fraction of year has passed
            expected_pace = (current_week / (current_week if use_ytd else 52)) * tgt_fob
            on_track = fob_cur >= expected_pace

            tgt_rows.append({
                "_country_raw":  c,
                "_fob_cur":      fob_cur,
                "_gap":          gap,
                "_pct_done":     pct_done,
                "_on_track":     on_track,
                "Country":       f"{flag(c)} {c}",
                f"FOB {py}":     f"$ {fob_prev:,.0f}" if fob_prev else "—",
                "Target %":      f"{tgt_pct:+.1f}%",
                "Target FOB":    f"$ {tgt_fob:,.0f}" if tgt_fob else "—",
                f"FOB {cy}":     f"$ {fob_cur:,.0f}",
                "% of Target":   f"{pct_done:.1f}%",
                "Gap":           f"✓ ahead $ {abs(gap):,.0f}" if gap <= 0 else f"▼ $ {gap:,.0f}",
                "Pace":          "✓ On track" if on_track else "⚠ Behind",
            })

        tgt_rows.sort(key=lambda x: x["_fob_cur"], reverse=True)
        display_cols = ["Country", f"FOB {py}", "Target %", "Target FOB", f"FOB {cy}", "% of Target", "Gap", "Pace"]
        st.dataframe(pd.DataFrame(tgt_rows)[display_cols], use_container_width=True, hide_index=True)

        # Summary KPIs
        divider()
        on_track_n  = sum(1 for r in tgt_rows if r["_on_track"])
        behind_n    = len(tgt_rows) - on_track_n
        total_tgt   = sum(safe_float(r["_gap"]) for r in tgt_rows if r["_gap"] > 0)
        total_ahead = sum(abs(safe_float(r["_gap"])) for r in tgt_rows if r["_gap"] <= 0)
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("Countries tracked", f"{len(tgt_rows)}")
        s2.metric("On track",          f"{on_track_n}", delta=f"{behind_n} behind")
        s3.metric("Total gap to close", f"$ {total_tgt:,.0f}")
        s4.metric("Total ahead",        f"$ {total_ahead:,.0f}")

        divider()

        # Per-country pace chart (cumulative FOB vs target pace line)
        section_label("Cumulative Pace per Country", "#4A6080")
        info_strip("Each chart shows the actual cumulative FOB week by week vs the linear target pace needed to hit the annual goal.", "#4A6080")

        pace_countries = [r["_country_raw"] for r in tgt_rows if targets.get(r["_country_raw"], 0) != 0][:12]
        if pace_countries and not prev_df.empty:
            n_pace_cols = 2
            pace_chunks = [pace_countries[i:i+n_pace_cols] for i in range(0, len(pace_countries), n_pace_cols)]
            max_week_axis = current_week if use_ytd else 52

            for chunk in pace_chunks:
                cols = st.columns(n_pace_cols)
                for col, country in zip(cols, chunk):
                    row = cntry_base[cntry_base["country"]==country]
                    if row.empty: continue
                    fob_prev_c = safe_float(row["fob_prev"].values[0])
                    tgt_pct_c  = safe_float(targets.get(country, 10.0))
                    tgt_fob_c  = fob_prev_c * (1 + tgt_pct_c/100)

                    # Actual weekly cumulative
                    wk_c = cur_df[cur_df["country"]==country].groupby("delivery_week").agg(fob=("total_price","sum")).reset_index().sort_values("delivery_week")
                    wk_c["cumulative"] = wk_c["fob"].cumsum()

                    all_wks = list(range(1, max_week_axis+1))
                    pace_line = [tgt_fob_c * (w / max_week_axis) for w in all_wks]

                    fig_cp = go.Figure()
                    fig_cp.add_trace(go.Scatter(
                        x=wk_c["delivery_week"], y=wk_c["cumulative"],
                        name="Actual", line=dict(color="#8C3D3D", width=2.5),
                        mode="lines+markers", marker_size=4, fill="tozeroy",
                        fillcolor="rgba(140,61,61,0.07)"))
                    fig_cp.add_trace(go.Scatter(
                        x=all_wks, y=pace_line,
                        name=f"Target ({tgt_pct_c:+.0f}%)",
                        line=dict(color="#2D4A3E", width=1.5, dash="dash"),
                        mode="lines"))
                    fig_cp.update_yaxes(tickprefix="$ ", tickfont=dict(size=9, color="#4A4A4A"), gridcolor="#F0EDE8")
                    fig_cp.update_xaxes(title="Week", tickfont=dict(size=9, color="#4A4A4A"), gridcolor="#F0EDE8")
                    fig_cp.update_layout(
                        title=dict(text=f"{flag(country)} {country}", font=dict(family="Cormorant Garamond", size=14, color="#1A1A1A")),
                        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                        font_family="Jost", margin=dict(l=0,r=0,t=32,b=0),
                        height=220, showlegend=False)
                    col.plotly_chart(fig_cp, use_container_width=True)
        else:
            st.info("Set targets above and ensure prior-year data is available to see pace charts.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — CUSTOMER INTELLIGENCE
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[2]:

        # ── Concentration ────────────────────────────────────────────────────
        section_label("Customer Concentration & Dependency Risk", "#8C3D3D")
        info_strip(
            "High concentration in few customers = high revenue risk. "
            "A healthy portfolio spreads FOB across many accounts.", "#8C3D3D")

        cust_fob = cur_df.groupby("customer_name").agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique"),
            units=("total_quantity","sum"), countries=("country","nunique")).reset_index()
        cust_fob = cust_fob.sort_values("fob", ascending=False).reset_index(drop=True)
        total_fob_cur = safe_float(cust_fob["fob"].sum())
        cust_fob["share_%"]      = cust_fob["fob"] / total_fob_cur * 100 if total_fob_cur else 0
        cust_fob["cumulative_%"] = cust_fob["share_%"].cumsum()

        top80 = int((cust_fob["cumulative_%"] <= 80).sum()) + 1
        info_strip(
            f"<strong>{top80} customer{'s' if top80!=1 else ''}</strong> account for 80% of current-year FOB. "
            f"Total active customers: <strong>{len(cust_fob)}</strong>.", "#4A6080")

        fig_conc = px.bar(
            cust_fob.head(20), x="customer_name", y="fob",
            labels={"customer_name":"Customer","fob":"FOB (USD)"},
            color="share_%",
            color_continuous_scale=["#F0EAE2","#8C3D3D"])
        fig_conc.update_yaxes(tickprefix="$ ")
        fig_conc.update_xaxes(tickangle=-35)
        fig_conc.update_coloraxes(colorbar_title="Share %")
        plotly_layout(fig_conc, height=320)
        st.plotly_chart(fig_conc, use_container_width=True)

        divider()

        # ── Top growing / declining ──────────────────────────────────────────
        section_label("Top Growing & Declining Customers", "#2D4A3E")
        if not prev_df.empty:
            cust_prev = prev_df.groupby("customer_name").agg(fob_prev=("total_price","sum")).reset_index()
            cust_comp = cust_fob[["customer_name","fob"]].merge(cust_prev, on="customer_name", how="outer").fillna(0)
            cust_comp["chg_pct"] = cust_comp.apply(lambda r: pct_change(r["fob"], r["fob_prev"]), axis=1)
            cust_comp = cust_comp[cust_comp["fob"] > 0].dropna(subset=["chg_pct"])
            cust_comp = cust_comp.sort_values("chg_pct", ascending=False)
            top5 = cust_comp.head(5)
            bot5 = cust_comp.tail(5).sort_values("chg_pct")

            cg1, cg2 = st.columns(2)
            def ranked_list(col, title, color, rows_df):
                col.markdown(
                    f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;'
                    f'text-transform:uppercase;color:{color};margin-bottom:10px;'
                    f'border-bottom:2px solid {color};padding-bottom:6px;">{title}</div>',
                    unsafe_allow_html=True)
                for i, (_, r) in enumerate(rows_df.iterrows(), 1):
                    col.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;padding:9px 0;'
                        f'border-bottom:1px solid #EDE9E3;">'
                        f'<span style="font-family:Cormorant Garamond,serif;font-size:1.1rem;'
                        f'font-weight:500;color:{color};min-width:20px;">{i}</span>'
                        f'<span style="font-family:Jost,sans-serif;font-size:.84rem;color:#1A1A1A;flex:1;">'
                        f'{r["customer_name"]}</span>'
                        f'<div style="text-align:right;">'
                        f'<div style="font-family:Jost,sans-serif;font-size:.82rem;font-weight:500;color:{color};">'
                        f'{r["chg_pct"]:+.1f}%</div>'
                        f'<div style="font-family:Jost,sans-serif;font-size:.72rem;color:#7A7A7A;">'
                        f'$ {safe_float(r["fob"]):,.0f}</div>'
                        f'</div></div>',
                        unsafe_allow_html=True)
            ranked_list(cg1, "Top 5 Growing",   "#2D4A3E", top5)
            ranked_list(cg2, "Top 5 Declining", "#8C3D3D", bot5)
        else:
            st.info("Need prior-year data to show growth/decline rankings.")

        divider()

        # ── Weekly run-rate ──────────────────────────────────────────────────
        section_label(f"Weekly Run-Rate  ·  {cur_year} vs {prev_year}", "#4A6080")
        info_strip(
            f"Compare each individual week this year against the same week last year — "
            f"spot exactly which weeks are ahead or behind.", "#4A6080")

        if not prev_df.empty:
            wk_cur  = cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_prev = prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_rr   = wk_cur.merge(wk_prev, on="delivery_week", how="outer").fillna(0).sort_values("delivery_week")
            wk_rr["diff"] = wk_rr["fob_cur"] - wk_rr["fob_prev"]

            fig_rr = go.Figure()
            fig_rr.add_bar(x=wk_rr["delivery_week"], y=wk_rr["fob_prev"],
                           name=str(prev_year), marker_color="#DDD8D0")
            fig_rr.add_bar(x=wk_rr["delivery_week"], y=wk_rr["fob_cur"],
                           name=str(cur_year), marker_color="#8C3D3D",
                           opacity=0.85)
            fig_rr.update_layout(barmode="overlay")
            fig_rr.update_yaxes(tickprefix="$ ")
            fig_rr.update_xaxes(title="ISO Week")
            plotly_layout(fig_rr, height=300)
            st.plotly_chart(fig_rr, use_container_width=True)

            # Difference table
            wk_rr["Week"]       = wk_rr["delivery_week"].apply(lambda w: f"W{int(w)}")
            wk_rr[f"FOB {cy}"]  = wk_rr["fob_cur"].apply(lambda x: f"$ {x:,.0f}")
            wk_rr[f"FOB {py}"]  = wk_rr["fob_prev"].apply(lambda x: f"$ {x:,.0f}")
            wk_rr["Difference"] = wk_rr["diff"].apply(
                lambda x: f"▲ $ {abs(x):,.0f}" if x >= 0 else f"▼ $ {abs(x):,.0f}")
            st.dataframe(
                wk_rr[["Week", f"FOB {cy}", f"FOB {py}", "Difference"]],
                use_container_width=True, hide_index=True)
        else:
            st.info(f"No {prev_year} data available for run-rate comparison.")

        divider()

        # ── New customer tracking ────────────────────────────────────────────
        section_label("New Customer Tracking", "#B8924A")
        info_strip(
            f"Customers with no activity in any prior year — tracked from their first order. "
            f"Monitor their trajectory to assess retention potential.", "#B8924A")

        all_prev_custs = dff[dff["delivery_year"] < cur_year]["customer_name"].unique()
        new_custs_df   = cur_df[~cur_df["customer_name"].isin(all_prev_custs)]

        if not new_custs_df.empty:
            nc_grp = new_custs_df.groupby("customer_name").agg(
                first_week=("delivery_week","min"),
                last_week=("delivery_week","max"),
                weeks_active=("delivery_week","nunique"),
                fob=("total_price","sum"),
                ships=("shipment_id","nunique"),
                countries=("country", lambda x: ", ".join(f"{flag(c)} {c}" for c in sorted(x.unique())))).reset_index()
            nc_grp = nc_grp.sort_values("fob", ascending=False)
            nc_grp["FOB"]        = nc_grp["fob"].apply(lambda x: f"$ {x:,.0f}")
            nc_grp["Avg FOB/wk"] = nc_grp.apply(
                lambda r: f"$ {safe_float(r['fob'])/max(safe_int(r['weeks_active']),1):,.0f}", axis=1)

            st.dataframe(
                nc_grp[["customer_name","first_week","last_week","weeks_active",
                        "ships","FOB","Avg FOB/wk","countries"]].rename(columns={
                    "customer_name":"Customer","first_week":"First Week",
                    "last_week":"Last Week","weeks_active":"Active Weeks",
                    "ships":"Shipments","countries":"Countries"}),
                use_container_width=True, hide_index=True)

            # Trajectory sparklines — top 8 new customers
            divider()
            section_label(f"New Customer Weekly Trajectory  ·  {cur_year}", "#B8924A")
            top_new = nc_grp.head(8)["customer_name"].tolist()
            nc_wk   = new_custs_df[new_custs_df["customer_name"].isin(top_new)].groupby(
                ["customer_name","delivery_week"]).agg(fob=("total_price","sum")).reset_index()

            if not nc_wk.empty:
                n_sp_cols = 4
                sp_chunks = [top_new[i:i+n_sp_cols] for i in range(0, len(top_new), n_sp_cols)]
                for chunk in sp_chunks:
                    cols = st.columns(n_sp_cols)
                    for col, cname in zip(cols, chunk):
                        cd = nc_wk[nc_wk["customer_name"]==cname].sort_values("delivery_week")
                        if cd.empty: continue
                        ttl = safe_float(cd["fob"].sum())
                        fig_sp = go.Figure()
                        fig_sp.add_trace(go.Bar(
                            x=cd["delivery_week"], y=cd["fob"],
                            marker_color="#B8924A", opacity=0.85))
                        fig_sp.update_layout(
                            title=dict(text=f"{cname[:18]}<br><span style='font-size:10px;'>$ {ttl:,.0f}</span>",
                                       font=dict(family="Jost", size=11, color="#1A1A1A")),
                            plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0,r=0,t=40,b=0), height=160, showlegend=False)
                        fig_sp.update_yaxes(tickprefix="$ ", tickfont=dict(size=8), gridcolor="#F0EDE8", showgrid=True)
                        fig_sp.update_xaxes(tickfont=dict(size=8), title="")
                        col.plotly_chart(fig_sp, use_container_width=True)
        else:
            st.info(f"No new customers found in {cur_year} compared to prior years.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — SEASONALITY
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[3]:
        section_label(f"Seasonality Heatmap  ·  FOB by Country & Week  ·  {cur_year}", "#4A6080")
        info_strip(
            "Which weeks are your strongest per market? "
            "Use this to plan commercial push timing, inventory, and staffing.", "#4A6080")

        season = cur_df.groupby(["country","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        if not season.empty:
            heat_piv = season.pivot_table(
                index="country", columns="delivery_week", values="fob", aggfunc="sum").fillna(0)
            top_countries_s = heat_piv.sum(axis=1).nlargest(15).index
            heat_piv = heat_piv.loc[top_countries_s]
            heat_piv.index = [f"{flag(c)} {c}" for c in heat_piv.index]

            fig_sea = go.Figure(data=go.Heatmap(
                z=heat_piv.values,
                x=[f"W{int(w)}" for w in heat_piv.columns],
                y=heat_piv.index.tolist(),
                colorscale=[[0,"#F5F2ED"],[0.25,"#F0EAE2"],[0.6,"#C47A7A"],[1,"#5C1F1F"]],
                hoverongaps=False,
                hovertemplate="Country: %{y}<br>Week: %{x}<br>FOB: $ %{z:,.0f}<extra></extra>",
            ))
            fig_sea.update_layout(
                plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                font_family="Jost", font_color="#1A1A1A",
                margin=dict(l=0,r=0,t=16,b=0),
                height=max(320, len(top_countries_s)*34),
                xaxis=dict(side="top", tickfont=dict(size=10, color="#4A4A4A")),
                yaxis=dict(tickfont=dict(size=11, color="#1A1A1A")),
            )
            st.plotly_chart(fig_sea, use_container_width=True)

        divider()
        section_label(f"Strongest Weeks Overall  ·  {cur_year}")
        wk_total = cur_df.groupby("delivery_week").agg(
            fob=("total_price","sum"),
            ships=("shipment_id","nunique"),
            customers=("customer_name","nunique")).reset_index()
        wk_total = wk_total.sort_values("fob", ascending=False).head(10)
        wk_total["Week"]      = wk_total["delivery_week"].apply(lambda w: week_label(cur_year, int(w)))
        wk_total["FOB"]       = wk_total["fob"].apply(lambda x: f"$ {x:,.0f}")
        wk_total["Shipments"] = wk_total["ships"]
        wk_total["Customers"] = wk_total["customers"]
        st.dataframe(wk_total[["Week","FOB","Shipments","Customers"]],
                     use_container_width=True, hide_index=True)

        if not prev_df.empty:
            divider()
            section_label(f"Same-Week Comparison  ·  {cur_year} vs {prev_year}")
            wk_cp = cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_pp = prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_mrg= wk_cp.merge(wk_pp, on="delivery_week", how="outer").fillna(0).sort_values("delivery_week")

            fig_wk = go.Figure()
            fig_wk.add_trace(go.Scatter(
                x=wk_mrg["delivery_week"], y=wk_mrg["fob_prev"],
                name=str(prev_year), line=dict(color="#DDD8D0", width=2), mode="lines"))
            fig_wk.add_trace(go.Scatter(
                x=wk_mrg["delivery_week"], y=wk_mrg["fob_cur"],
                name=str(cur_year), line=dict(color="#8C3D3D", width=2.5),
                mode="lines+markers", marker_size=4))
            fig_wk.update_yaxes(tickprefix="$ ")
            fig_wk.update_xaxes(title="ISO Week")
            plotly_layout(fig_wk, height=300)
            st.plotly_chart(fig_wk, use_container_width=True)

            divider()
            section_label(f"Country Seasonality Shift  ·  {cur_year} vs {prev_year}")
            info_strip("Which countries changed their active season? Darker cells = higher FOB that week.", "#4A6080")

            prev_heat = prev_df.groupby(["country","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
            if not prev_heat.empty:
                ph_piv = prev_heat.pivot_table(
                    index="country", columns="delivery_week", values="fob", aggfunc="sum").fillna(0)
                common_c = [c for c in heat_piv.index if c.split(" ",1)[-1] in ph_piv.index] if not season.empty else []

                if common_c and not season.empty:
                    # Build shift: current - previous (normalised)
                    cur_norm  = heat_piv.loc[common_c] if common_c else heat_piv
                    prev_sub  = ph_piv.loc[[c.split(" ",1)[-1] for c in common_c if c.split(" ",1)[-1] in ph_piv.index]]
                    if not prev_sub.empty:
                        prev_sub.index = [f"{flag(c)} {c}" for c in prev_sub.index]
                        common_weeks = sorted(set(cur_norm.columns) & set(prev_sub.columns))
                        shift_df = cur_norm[common_weeks] - prev_sub[common_weeks]

                        fig_shift = go.Figure(data=go.Heatmap(
                            z=shift_df.values,
                            x=[f"W{int(w)}" for w in shift_df.columns],
                            y=shift_df.index.tolist(),
                            colorscale=[
                                [0,"#8C3D3D"],[0.35,"#F0EAE2"],
                                [0.5,"#F5F2ED"],[0.65,"#C8DDD0"],[1,"#2D4A3E"]],
                            zmid=0,
                            hoverongaps=False,
                            hovertemplate="Country: %{y}<br>Week: %{x}<br>Δ FOB: $ %{z:,.0f}<extra></extra>",
                        ))
                        fig_shift.update_layout(
                            plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                            font_family="Jost", font_color="#1A1A1A",
                            margin=dict(l=0,r=0,t=16,b=0),
                            height=max(280, len(shift_df)*34),
                            xaxis=dict(side="top", tickfont=dict(size=10, color="#4A4A4A")),
                            yaxis=dict(tickfont=dict(size=11, color="#1A1A1A")),
                        )
                        st.markdown(
                            '<div style="font-family:Jost,sans-serif;font-size:.72rem;color:#7A7A7A;'
                            'margin-bottom:8px;">Green = more FOB this year vs last year in that week  ·  '
                            'Red = less FOB  ·  White = no change</div>',
                            unsafe_allow_html=True)
                        st.plotly_chart(fig_shift, use_container_width=True)

    return  # end render_commercialimport streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import hashlib
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Export Operations Suite",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# AUTH — multi-user, works on Streamlit Cloud, self-hosted, and local
# ════════════════════════════════════════════════════════════════════════════
import json, os, pathlib

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()

# ── User store: secrets (cloud) → local JSON file → in-memory fallback ───────
USERS_FILE = pathlib.Path(".streamlit/users.json")

def _load_users() -> dict:
    """
    Priority:
    1. st.secrets["users"] — Streamlit Cloud / secrets.toml
    2. .streamlit/users.json — self-hosted / local persistent file
    3. st.session_state["_users_mem"] — in-memory fallback (resets on restart)
    Returns dict: {username_lower: {"hash": ..., "display": ..., "role": ...}}
    """
    # 1 — Streamlit secrets
    try:
        raw = st.secrets["users"]
        # Support both flat {user: hash} and rich {user: {hash, display, role}}
        out = {}
        for u, v in raw.items():
            u = u.lower()
            if isinstance(v, str):
                out[u] = {"hash": v, "display": u.title(), "role": "user"}
            else:
                out[u] = {
                    "hash":    v.get("hash", ""),
                    "display": v.get("display", u.title()),
                    "role":    v.get("role", "user"),
                }
        if out:
            return out
    except Exception:
        pass

    # 2 — Local JSON file
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text())
        except Exception:
            pass

    # 3 — In-memory (seeded with default admin on first run)
    if "_users_mem" not in st.session_state:
        st.session_state["_users_mem"] = {
            "admin": {
                "hash":    hash_pw("admin123"),
                "display": "Administrator",
                "role":    "admin",
            }
        }
    return st.session_state["_users_mem"]

def _save_users(users: dict):
    """Persist to file if possible; otherwise keep in memory."""
    st.session_state["_users_mem"] = users
    try:
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        USERS_FILE.write_text(json.dumps(users, indent=2))
    except Exception:
        pass  # read-only filesystem (Streamlit Cloud) — memory only

def check_credentials(username: str, password: str) -> bool:
    users = _load_users()
    u = username.strip().lower()
    if u not in users:
        return False
    return users[u]["hash"] == hash_pw(password)

def get_user(username: str) -> dict:
    users = _load_users()
    return users.get(username.strip().lower(),
                     {"display": username.title(), "role": "user"})

# ── Login screen ──────────────────────────────────────────────────────────────
def render_login():
    components.html("""<style>
    html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],
    [data-testid="stMainBlockContainer"],.block-container{
      background-color:#F5F2ED!important;}
    </style>""", height=0)

    st.markdown("""
    <div style="text-align:center;padding:70px 0 36px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;
                  color:#1A1A1A;letter-spacing:.02em;line-height:1.2;">✦ Export Ops</div>
      <div style="font-family:'Jost',sans-serif;font-size:.65rem;letter-spacing:.22em;
                  text-transform:uppercase;color:#7A7A7A;margin-top:6px;">Management Suite</div>
    </div>""", unsafe_allow_html=True)

    _, card, _ = st.columns([1, 3, 1])
    with card:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;
                    padding:36px 32px 8px 32px;margin-bottom:0;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;
                      font-weight:500;color:#1A1A1A;margin-bottom:4px;">Sign in</div>
          <div style="font-family:'Jost',sans-serif;font-size:.78rem;color:#7A7A7A;
                      margin-bottom:20px;">Enter your credentials to continue</div>
        </div>""", unsafe_allow_html=True)

        with st.container():
            st.markdown('<div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:none;padding:0 32px 28px 32px;">', unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="username", key="login_user")
            password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pw")

            if st.session_state.get("login_failed"):
                st.markdown("""
                <div style="font-family:'Jost',sans-serif;font-size:.78rem;color:#8C3D3D;
                            padding:10px 14px;background:#FFF5F5;border-left:3px solid #8C3D3D;
                            margin-bottom:12px;">
                  Incorrect username or password.
                </div>""", unsafe_allow_html=True)

            if st.button("Sign In  →", use_container_width=True, key="login_btn"):
                if check_credentials(username, password):
                    st.session_state.update({
                        "authenticated": True,
                        "username":      username.strip().lower(),
                        "login_failed":  False,
                    })
                    st.rerun()
                else:
                    st.session_state["login_failed"] = True
                    st.rerun()

            st.markdown("""
            <div style="font-family:'Jost',sans-serif;font-size:.70rem;color:#9A9A9A;
                        text-align:center;margin-top:18px;line-height:1.7;">
              Access restricted to authorised personnel.
            </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── Admin panel ───────────────────────────────────────────────────────────────
def render_admin():
    page_header("User Management", "Add · Edit · Remove Users")
    users = _load_users()

    # ── Current users table ───────────────────────────────────────────────────
    section_label("Current Users", "#8C3D3D")
    rows = [{"Username": u,
             "Display Name": v["display"],
             "Role": v["role"]}
            for u, v in users.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    divider()

    # ── Add / edit user ───────────────────────────────────────────────────────
    section_label("Add or Update User", "#2D4A3E")
    col1, col2, col3, col4 = st.columns(4)
    new_user    = col1.text_input("Username",     key="adm_user",    placeholder="e.g. maria")
    new_display = col2.text_input("Display Name", key="adm_display", placeholder="e.g. María García")
    new_pw      = col3.text_input("Password",     key="adm_pw",      type="password", placeholder="New password")
    new_role    = col4.selectbox("Role",          ["user", "admin"],  key="adm_role")

    if st.button("Save User", key="adm_save"):
        u = new_user.strip().lower()
        if not u:
            st.warning("Username cannot be empty.")
        elif not new_pw and u not in users:
            st.warning("Password required for new users.")
        else:
            users[u] = {
                "hash":    hash_pw(new_pw) if new_pw else users.get(u, {}).get("hash", ""),
                "display": new_display.strip() or u.title(),
                "role":    new_role,
            }
            _save_users(users)
            st.success(f"User **{u}** saved.")
            st.rerun()

    divider()

    # ── Delete user ───────────────────────────────────────────────────────────
    section_label("Remove User", "#B8924A")
    del_user = st.selectbox("Select user to remove",
                            [u for u in users if u != st.session_state.get("username")],
                            key="adm_del")
    if st.button("Remove User", key="adm_del_btn"):
        if del_user in users:
            del users[del_user]
            _save_users(users)
            st.success(f"User **{del_user}** removed.")
            st.rerun()

    divider()

    # ── Change own password ───────────────────────────────────────────────────
    section_label("Change My Password", "#4A6080")
    cp1, cp2 = st.columns(2)
    cur_pw  = cp1.text_input("Current password", type="password", key="cp_cur")
    new_pw2 = cp2.text_input("New password",     type="password", key="cp_new")
    if st.button("Update Password", key="cp_btn"):
        me = st.session_state.get("username", "")
        if not check_credentials(me, cur_pw):
            st.error("Current password is incorrect.")
        elif len(new_pw2) < 6:
            st.warning("New password must be at least 6 characters.")
        else:
            users[me]["hash"] = hash_pw(new_pw2)
            _save_users(users)
            st.success("Password updated successfully.")

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    render_login()
    st.stop()


# ── Force light theme via config ─────────────────────────────────────────────
# Inject into .streamlit/config.toml equivalent via query params trick
components.html("""
<script>
// Force the page body and all Streamlit wrappers to light background
const style = document.createElement('style');
style.textContent = `
  body, #root, .main, .block-container,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stMain"],
  [data-testid="stMainBlockContainer"] {
    background-color: #F5F2ED !important;
    color: #1A1A1A !important;
  }
`;
document.head.appendChild(style);
</script>
""", height=0)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap');

/* ── Force light mode on every Streamlit container ── */
html,
body,
.main,
.block-container,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[class*="css"],
.element-container,
div[data-stale="false"] {
  background-color: #F5F2ED !important;
  color: #1A1A1A !important;
  font-family: 'Jost', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div {
  background-color: #5C1F1F !important;
}
section[data-testid="stSidebar"] * {
  color: #F5EDE8 !important;
}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSelectbox label {
  color: #D4B8B0 !important;
  font-size: .72rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
  border: 1px dashed rgba(212,176,168,.45) !important;
  border-radius: 0 !important;
  background: rgba(255,255,255,.05) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
  color: #D4B8B0 !important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  color: #F5EDE8 !important;
  font-size: .84rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="popover"] {
  background-color: #3D1010 !important;
  border-color: rgba(212,176,168,.3) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
  background: #FFFFFF !important;
  border: 1px solid #DDD8D0 !important;
  border-top: 3px solid #8C3D3D !important;
  border-radius: 0 !important;
  padding: 20px 24px !important;
}
[data-testid="metric-container"] label {
  font-family: 'Jost', sans-serif !important;
  font-size: .65rem !important;
  letter-spacing: .18em !important;
  text-transform: uppercase !important;
  color: #7A7A7A !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 2.2rem !important;
  font-weight: 500 !important;
  color: #1A1A1A !important;
  line-height: 1.15 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-family: 'Jost', sans-serif !important;
  font-size: .78rem !important;
  font-weight: 500 !important;
  color: #1A1A1A !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid #DDD8D0 !important;
  border-radius: 0 !important;
}
[data-testid="stDataFrame"] * {
  color: #1A1A1A !important;
  background-color: #FFFFFF !important;
}

/* ── Buttons ── */
.stButton > button {
  background-color: #8C3D3D !important;
  color: #FFF5F0 !important;
  border: none !important;
  font-family: 'Jost', sans-serif !important;
  font-size: .72rem !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 10px 28px !important;
}
.stButton > button:hover { background-color: #5C1F1F !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
  background-color: #FFFFFF !important;
  color: #8C3D3D !important;
  border: 1px solid #8C3D3D !important;
  font-family: 'Jost', sans-serif !important;
  font-size: .70rem !important;
  letter-spacing: .14em !important;
  text-transform: uppercase !important;
  border-radius: 0 !important;
  padding: 8px 22px !important;
}
[data-testid="stDownloadButton"] button:hover {
  background-color: #8C3D3D !important;
  color: #FFFFFF !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #F5F2ED !important;
  border-bottom: 1px solid #DDD8D0 !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Jost', sans-serif !important;
  font-size: .68rem !important;
  letter-spacing: .13em !important;
  text-transform: uppercase !important;
  color: #7A7A7A !important;
  padding: 12px 22px !important;
  border-bottom: 2px solid transparent !important;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #8C3D3D !important;
  border-bottom: 2px solid #8C3D3D !important;
  font-weight: 500 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background-color: #F5F2ED !important;
  padding-top: 20px !important;
}

/* ── Expander ── */
details,
[data-testid="stExpander"] {
  border: 1px solid #DDD8D0 !important;
  border-radius: 0 !important;
  margin-bottom: 6px !important;
  background: #FFFFFF !important;
}
[data-testid="stExpander"] summary,
details summary {
  font-family: 'Jost', sans-serif !important;
  font-size: .78rem !important;
  letter-spacing: .06em !important;
  color: #1A1A1A !important;
  background: #FFFFFF !important;
  padding: 12px 16px !important;
}
[data-testid="stExpander"][open] summary,
details[open] summary { color: #8C3D3D !important; }
[data-testid="stExpander"] > div > div {
  background: #FFFFFF !important;
  padding: 0 16px 12px !important;
}

/* ── Multiselect ── */
.stMultiSelect [data-baseweb="tag"] {
  background-color: #F0EAE2 !important;
  color: #5C1F1F !important;
  border-radius: 0 !important;
}
[data-baseweb="select"] > div {
  background-color: #FFFFFF !important;
  border-color: #DDD8D0 !important;
  color: #1A1A1A !important;
}

/* ── Input/select text ── */
input, textarea, [data-baseweb="input"] * {
  background-color: #FFFFFF !important;
  color: #1A1A1A !important;
}

/* ── Radio ── */
[data-testid="stRadio"] > label {
  color: #1A1A1A !important;
}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
  color: #1A1A1A !important;
}

/* ── Alerts ── */
.stAlert {
  border-radius: 0 !important;
  background-color: #FFF8F5 !important;
  color: #1A1A1A !important;
}

/* ── Headers & text ── */
h1, h2, h3, h4, h5, h6, p, span, div, label {
  color: #1A1A1A !important;
}

/* ── Plotly chart bg ── */
.js-plotly-plot, .plotly, .plot-container {
  background: transparent !important;
}
</style>
"""
components.html(CSS, height=0)

# ── IATA → Country ────────────────────────────────────────────────────────────
IATA_COUNTRY = {
    "JFK":"United States","MIA":"United States","LAX":"United States","ORD":"United States",
    "ATL":"United States","BOS":"United States","DFW":"United States","SFO":"United States",
    "EWR":"United States","IAD":"United States","SEA":"United States","PHL":"United States",
    "DTW":"United States","MSP":"United States","CLT":"United States","LGA":"United States",
    "MDW":"United States","BWI":"United States","DEN":"United States","MCO":"United States",
    "YYZ":"Canada","YVR":"Canada","YUL":"Canada","YYC":"Canada","YEG":"Canada",
    "MEX":"Mexico","GDL":"Mexico","MTY":"Mexico","CUN":"Mexico",
    "PTY":"Panama","SJO":"Costa Rica","GUA":"Guatemala","SAL":"El Salvador",
    "MBJ":"Jamaica","KIN":"Jamaica","NAS":"Bahamas","PUJ":"Dominican Republic",
    "SDQ":"Dominican Republic","SJU":"Puerto Rico","HAV":"Cuba",
    "GRU":"Brazil","GIG":"Brazil","VCP":"Brazil","BSB":"Brazil","SSA":"Brazil",
    "BOG":"Colombia","MDE":"Colombia","CTG":"Colombia","CLO":"Colombia","BAQ":"Colombia",
    "UIO":"Ecuador","GYE":"Ecuador","LIM":"Peru","CUZ":"Peru",
    "SCL":"Chile","EZE":"Argentina","AEP":"Argentina","MVD":"Uruguay","ASU":"Paraguay",
    "LPB":"Bolivia","CCS":"Venezuela",
    "AMS":"Netherlands","LHR":"United Kingdom","LGW":"United Kingdom","MAN":"United Kingdom",
    "CDG":"France","ORY":"France","NCE":"France",
    "FRA":"Germany","MUC":"Germany","DUS":"Germany","HAM":"Germany","BER":"Germany",
    "MAD":"Spain","BCN":"Spain","VLC":"Spain",
    "FCO":"Italy","MXP":"Italy","VCE":"Italy",
    "ZRH":"Switzerland","GVA":"Switzerland","VIE":"Austria","BRU":"Belgium",
    "CPH":"Denmark","ARN":"Sweden","OSL":"Norway","HEL":"Finland",
    "LIS":"Portugal","ATH":"Greece","WAW":"Poland","PRG":"Czech Republic",
    "BUD":"Hungary","ZAG":"Croatia","SOF":"Bulgaria","OTP":"Romania",
    "IST":"Turkey","SAW":"Turkey",
    "DXB":"United Arab Emirates","AUH":"United Arab Emirates","SHJ":"United Arab Emirates",
    "DOH":"Qatar","BAH":"Bahrain","KWI":"Kuwait","MCT":"Oman",
    "TLV":"Israel","RUH":"Saudi Arabia","JED":"Saudi Arabia",
    "CAI":"Egypt","NBO":"Kenya","JNB":"South Africa","CPT":"South Africa",
    "ADD":"Ethiopia","KGL":"Rwanda","LOS":"Nigeria","ACC":"Ghana","CMN":"Morocco",
    "HKG":"Hong Kong","SIN":"Singapore","KUL":"Malaysia",
    "NRT":"Japan","HND":"Japan","KIX":"Japan",
    "ICN":"South Korea","PEK":"China","PVG":"China","CAN":"China",
    "TPE":"Taiwan","BKK":"Thailand","CGK":"Indonesia","DPS":"Indonesia",
    "MNL":"Philippines","SGN":"Vietnam","HAN":"Vietnam",
    "BOM":"India","DEL":"India","BLR":"India",
    "SYD":"Australia","MEL":"Australia","BNE":"Australia","AKL":"New Zealand",
}
COUNTRY_FLAG = {
    "United States":"🇺🇸","Canada":"🇨🇦","Mexico":"🇲🇽","Brazil":"🇧🇷","Colombia":"🇨🇴",
    "Ecuador":"🇪🇨","Peru":"🇵🇪","Chile":"🇨🇱","Argentina":"🇦🇷","Uruguay":"🇺🇾",
    "Paraguay":"🇵🇾","Bolivia":"🇧🇴","Venezuela":"🇻🇪","Panama":"🇵🇦","Costa Rica":"🇨🇷",
    "Guatemala":"🇬🇹","El Salvador":"🇸🇻","Honduras":"🇭🇳","Nicaragua":"🇳🇮",
    "Jamaica":"🇯🇲","Dominican Republic":"🇩🇴","Puerto Rico":"🇵🇷","Cuba":"🇨🇺","Bahamas":"🇧🇸",
    "Netherlands":"🇳🇱","United Kingdom":"🇬🇧","France":"🇫🇷","Germany":"🇩🇪","Spain":"🇪🇸",
    "Italy":"🇮🇹","Switzerland":"🇨🇭","Austria":"🇦🇹","Belgium":"🇧🇪","Denmark":"🇩🇰",
    "Sweden":"🇸🇪","Norway":"🇳🇴","Finland":"🇫🇮","Portugal":"🇵🇹","Greece":"🇬🇷",
    "Poland":"🇵🇱","Czech Republic":"🇨🇿","Hungary":"🇭🇺","Romania":"🇷🇴","Bulgaria":"🇧🇬",
    "Croatia":"🇭🇷","Turkey":"🇹🇷","Ukraine":"🇺🇦",
    "United Arab Emirates":"🇦🇪","Qatar":"🇶🇦","Saudi Arabia":"🇸🇦","Kuwait":"🇰🇼",
    "Bahrain":"🇧🇭","Oman":"🇴🇲","Israel":"🇮🇱",
    "Egypt":"🇪🇬","Kenya":"🇰🇪","South Africa":"🇿🇦","Ethiopia":"🇪🇹","Nigeria":"🇳🇬",
    "Ghana":"🇬🇭","Morocco":"🇲🇦","Rwanda":"🇷🇼",
    "Japan":"🇯🇵","South Korea":"🇰🇷","China":"🇨🇳","Hong Kong":"🇭🇰","Taiwan":"🇹🇼",
    "Singapore":"🇸🇬","Thailand":"🇹🇭","Malaysia":"🇲🇾","Indonesia":"🇮🇩","Philippines":"🇵🇭",
    "Vietnam":"🇻🇳","India":"🇮🇳","Australia":"🇦🇺","New Zealand":"🇳🇿",
}

REQUIRED_COLS = ["delivery_year","delivery_week","customer_name",
                 "supply_source_name","destination","total_quantity","total_price"]
SHIPMENT_KEYS = ["customer_name","delivery_year","delivery_week","supply_source_name","iata_code"]

# Countries excluded from all analysis (transit hubs / non-end-markets)
EXCLUDED_COUNTRIES = {"Netherlands", "Kenya", "Canada"}

# Plotly palette — all high-contrast on white background
PALETTE = ["#8C3D3D","#2D4A3E","#B8924A","#4A6080","#6B4080","#2D6B5A","#80502D"]

# ── Utility helpers ───────────────────────────────────────────────────────────
def flag(c): return COUNTRY_FLAG.get(c, "🌍")

def safe_int(v):
    try:
        f = float(v)
        return 0 if (np.isnan(f) or np.isinf(f)) else int(f)
    except Exception:
        return 0

def safe_float(v):
    try:
        f = float(v)
        return 0.0 if (np.isnan(f) or np.isinf(f)) else f
    except Exception:
        return 0.0

def pct_change(cur, prev):
    c, p = safe_float(cur), safe_float(prev)
    if p == 0: return None
    return (c - p) / p * 100

def status_badge(chg, cur_fob):
    cf = safe_float(cur_fob)
    if chg is None:  return "🆕 New"
    if cf == 0:      return "⛔ Lost"
    if chg >= 15:    return "🚀 Strong growth"
    if chg >= 3:     return "🟢 Growing"
    if chg >= -5:    return "🟡 Stable"
    if chg >= -20:   return "🔻 Declining"
    return "🔴 At risk"

def safe_pivot_val(pivot_df, key_col, key_val, year_col):
    row = pivot_df[pivot_df[key_col] == key_val]
    if row.empty or year_col not in row.columns:
        return 0.0
    return safe_float(row[year_col].values[0])

# ── UI components ─────────────────────────────────────────────────────────────
def divider():
    st.markdown('<div style="border-top:1px solid #DDD8D0;margin:32px 0;"></div>', unsafe_allow_html=True)

def page_header(title, subtitle=""):
    st.markdown(f"""
    <div style="padding:40px 0 28px 0;border-bottom:1px solid #DDD8D0;margin-bottom:32px;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;
                  color:#1A1A1A;letter-spacing:.015em;line-height:1.15;">{title}</div>
      {"<div style='font-family:Jost,sans-serif;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#7A7A7A;margin-top:10px;'>" + subtitle + "</div>" if subtitle else ""}
    </div>""", unsafe_allow_html=True)

def section_label(text, accent="#8C3D3D"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin:28px 0 12px 0;">
      <div style="width:28px;height:1px;background:{accent};"></div>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:500;
                   color:#1A1A1A;letter-spacing:.03em;">{text}</span>
      <div style="flex:1;height:1px;background:#EDE9E3;"></div>
    </div>""", unsafe_allow_html=True)

def info_strip(msg, accent="#2D4A3E"):
    st.markdown(f"""
    <div style="background:#FFFFFF;border-left:3px solid {accent};
                padding:14px 20px;margin:10px 0 20px 0;
                font-family:'Jost',sans-serif;font-size:.83rem;
                color:#1A1A1A;line-height:1.8;
                box-shadow:0 1px 6px rgba(26,26,26,.05);">{msg}</div>""",
    unsafe_allow_html=True)

def country_strip(country, n_ship, fob, accent="#8C3D3D"):
    fl = flag(country)
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;
                padding:13px 20px;background:#FFFFFF;
                border-top:2px solid {accent};border-bottom:1px solid #EDE9E3;
                margin:20px 0 4px 0;box-shadow:0 2px 8px rgba(26,26,26,.04);">
      <span style="font-size:1.2rem;">{fl}</span>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;
                   font-weight:500;color:#1A1A1A;">{country}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.68rem;letter-spacing:.12em;
                   text-transform:uppercase;color:#7A7A7A;margin-left:6px;">
        {n_ship} shipment{"s" if n_ship!=1 else ""}
      </span>
      <span style="margin-left:auto;font-family:'Cormorant Garamond',serif;
                   font-size:1.1rem;color:{accent};font-weight:500;">
        $ {fob:,.0f}
      </span>
    </div>""", unsafe_allow_html=True)

def shipment_row(customer, origin, n_lines, units, fob, accent):
    st.markdown(f"""
    <div style="background:#FAFAF8;border-bottom:1px solid #EDE9E3;
                padding:10px 18px;display:flex;flex-wrap:wrap;align-items:center;gap:10px;">
      <span style="font-family:'Cormorant Garamond',serif;font-size:1rem;
                   font-weight:500;color:{accent};">📦 {customer}</span>
      <span style="font-family:'Jost',sans-serif;font-size:.72rem;
                   color:#7A7A7A;letter-spacing:.04em;">from {origin}</span>
      <span style="margin-left:auto;font-family:'Jost',sans-serif;
                   font-size:.72rem;color:#4A4A4A;letter-spacing:.03em;">
        {n_lines} line{"s" if n_lines!=1 else ""} &nbsp;·&nbsp;
        {units:,} units &nbsp;·&nbsp; $ {fob:,.2f}
      </span>
    </div>""", unsafe_allow_html=True)

def metric_delta_str(cur, prev):
    ch = pct_change(cur, prev)
    return f"{ch:+.1f}%" if ch is not None else None

# ── Plotly layout base ────────────────────────────────────────────────────────
def plotly_layout(fig, height=None):
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Jost",
        font_color="#1A1A1A",
        font_size=12,
        margin=dict(l=4, r=4, t=16, b=4),
        legend=dict(
            orientation="h", y=1.1, x=0,
            font=dict(size=11, color="#1A1A1A"),
            bgcolor="rgba(0,0,0,0)",
        ),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#EDE9E3", linecolor="#DDD8D0", tickcolor="#DDD8D0",
                     tickfont=dict(color="#4A4A4A", size=11))
    fig.update_yaxes(gridcolor="#EDE9E3", linecolor="#DDD8D0", tickcolor="#DDD8D0",
                     zeroline=False, tickfont=dict(color="#4A4A4A", size=11))
    if height:
        fig.update_layout(height=height)
    return fig

# ── Data loading ──────────────────────────────────────────────────────────────
def extract_iata(series):
    s = series.astype(str).str.upper().str.strip()
    extracted = s.str.extract(r'\b([A-Z]{3})\b', expand=False)
    return extracted.fillna(s.str[:3])

def load_and_validate(uploaded):
    try:
        df = pd.read_excel(uploaded, engine="openpyxl")
    except Exception as e:
        return None, f"Could not read file: {e}"
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return None, f"Missing required columns: **{', '.join(missing)}**"
    for opt in ["secondary_customer_name","crop_name","variety_name","order_type","product"]:
        if opt not in df.columns:
            df[opt] = ""
    df["delivery_year"]  = pd.to_numeric(df["delivery_year"],  errors="coerce")
    df["delivery_week"]  = pd.to_numeric(df["delivery_week"],  errors="coerce")
    df["total_quantity"] = pd.to_numeric(df["total_quantity"], errors="coerce").fillna(0)
    df["total_price"]    = pd.to_numeric(df["total_price"],    errors="coerce").fillna(0)
    df["iata_code"] = extract_iata(df["destination"])
    df["country"]   = df["iata_code"].map(IATA_COUNTRY).fillna("Unknown")
    df["shipment_id"] = (
        df["customer_name"].astype(str) + "|" +
        df["delivery_year"].astype(str) + "-W" +
        df["delivery_week"].astype(str).str.zfill(2) + "|" +
        df["supply_source_name"].astype(str) + "→" +
        df["iata_code"].astype(str)
    )
    return df, ""

def filter_week(df, year, week):
    return df[(df["delivery_year"]==year) & (df["delivery_week"]==week)]

def add_weeks(year, week, delta):
    import datetime as dt
    d = date.fromisocalendar(year, week, 1) + dt.timedelta(weeks=delta)
    iso = d.isocalendar()
    return iso[0], iso[1]

def week_label(y, w):
    try:
        d = date.fromisocalendar(y, w, 1)
        return d.strftime(f"Week {w}  ·  %b %d, {y}")
    except Exception:
        return f"Week {w} / {y}"

def apply_filters(df, origins, customers):
    if origins:   df = df[df["supply_source_name"].isin(origins)]
    if customers: df = df[df["customer_name"].isin(customers)]
    return df

def n_shipments(df):
    if df.empty: return 0
    return df.groupby(SHIPMENT_KEYS)["shipment_id"].nunique().sum()

# ════════════════════════════════════════════════════════════════════════════
# COMMERCIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
def render_commercial(df):
    import plotly.express as px
    import plotly.graph_objects as go

    years_avail   = sorted(df["delivery_year"].dropna().astype(int).unique())
    all_customers = sorted(df["customer_name"].dropna().unique())
    all_countries = sorted(c for c in df["country"].dropna().unique() if c not in EXCLUDED_COUNTRIES)

    page_header("Commercial Intelligence",
                "Year-over-Year Performance  ·  Growth Analysis  ·  Market Focus")

    ci_tabs = st.tabs([
        "📊  Overview & YoY",
        "🎯  Growth Targets",
        "👥  Customer Intelligence",
        "🌱  Product Mix",
        "📅  Seasonality",
        "🔗  Origin Mix",
    ])

    # ── Shared filters (above tabs) ───────────────────────────────────────────
    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]

    with st.expander("⚙  Filters & Scope", expanded=True):
        scope_col, note_col = st.columns([1, 2])
        with scope_col:
            scope = st.radio("Scope", ["📅  Year-to-Date", "📆  Full Year"], key="ci_scope")
        use_ytd = "Year-to-Date" in scope
        with note_col:
            if use_ytd:
                info_strip(f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. Prior years capped at week {current_week}.", "#2D4A3E")
            else:
                info_strip("Comparing <strong>all weeks in the system</strong> per year — including future confirmed orders.", "#B8924A")

        fc1, fc2, fc3 = st.columns(3)
        default_years = years_avail[-3:] if len(years_avail) >= 3 else years_avail
        sel_years     = fc1.multiselect("Years", years_avail, default=default_years, key="ci_years")
        sel_customers = fc2.multiselect("Customers", all_customers, default=[], key="ci_customers", placeholder="All customers")
        sel_countries = fc3.multiselect("Countries", all_countries, default=[], key="ci_countries", placeholder="All countries")

    if not sel_years:
        st.warning("Select at least one year.")
        return

    dff = df[df["delivery_year"].isin(sel_years)].copy()
    dff = dff[~dff["country"].isin(EXCLUDED_COUNTRIES)]
    if sel_customers: dff = dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff = dff[dff["country"].isin(sel_countries)]
    if use_ytd:       dff = dff[dff["delivery_week"] <= current_week]

    if dff.empty:
        st.info("No data matches the selected filters.")
        return

    cur_year   = max(sel_years)
    prev_year  = cur_year - 1
    prev2_year = cur_year - 2
    cy, py, p2y = str(cur_year), str(prev_year), str(prev2_year)
    scope_lbl = f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df   = dff[dff["delivery_year"]==cur_year]
    prev_df  = dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df = dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — OVERVIEW & YOY
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[0]:
        section_label(f"Summary  ·  {scope_lbl}  ·  {cur_year} vs {prev_year}")

        cur_ship  = n_shipments(cur_df)
        prev_ship = n_shipments(prev_df)
        cur_fob   = safe_float(cur_df["total_price"].sum())
        prev_fob  = safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
        cur_units = safe_float(cur_df["total_quantity"].sum())
        prev_units= safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0

        k1,k2,k3,k4 = st.columns(4)
        k1.metric("Shipments",        f"{cur_ship:,}",        delta=metric_delta_str(cur_ship,  prev_ship))
        k2.metric("FOB Value",        f"$ {cur_fob:,.0f}",    delta=metric_delta_str(cur_fob,   prev_fob))
        k3.metric("Units Shipped",    f"{int(cur_units):,}",  delta=metric_delta_str(cur_units, prev_units))
        k4.metric("Active Customers", f"{cur_df['customer_name'].nunique():,}")

        divider()
        section_label(f"Weekly FOB Trend  ·  {scope_lbl}")
        weekly = dff.groupby(["delivery_year","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        weekly["Year"] = weekly["delivery_year"].astype(str)
        fig_trend = px.line(weekly, x="delivery_week", y="fob", color="Year",
                            labels={"delivery_week":"ISO Week","fob":"FOB (USD)"},
                            color_discrete_sequence=PALETTE, markers=True)
        fig_trend.update_traces(line_width=2.5, marker_size=5)
        fig_trend.update_yaxes(tickprefix="$ ")
        plotly_layout(fig_trend, height=320)
        st.plotly_chart(fig_trend, use_container_width=True)

        divider()
        section_label(f"FOB by Country  ·  3-Year Comparison")
        cy_grp = dff.groupby(["country","delivery_year"]).agg(fob=("total_price","sum"), ships=("shipment_id","nunique")).reset_index()
        cy_grp["Year"]  = cy_grp["delivery_year"].astype(str)
        cy_grp["label"] = cy_grp["country"].apply(lambda c: f"{flag(c)} {c}")
        order = cy_grp[cy_grp["Year"]==cy].sort_values("fob", ascending=False)["country"].tolist()
        cy_grp["sort_key"] = cy_grp["country"].apply(lambda c: order.index(c) if c in order else 999)
        cy_grp = cy_grp.sort_values("sort_key")
        fig_cntry = px.bar(cy_grp, x="label", y="fob", color="Year", barmode="group",
                           labels={"label":"Country","fob":"FOB (USD)"},
                           color_discrete_sequence=PALETTE)
        fig_cntry.update_yaxes(tickprefix="$ ")
        fig_cntry.update_xaxes(tickangle=-35)
        plotly_layout(fig_cntry, height=360)
        st.plotly_chart(fig_cntry, use_container_width=True)

        divider()
        section_label(f"Country Status Table  ·  {scope_lbl}")
        piv_fob = cy_grp.pivot_table(index="country", columns="Year", values="fob",   aggfunc="sum").reset_index()
        piv_shp = cy_grp.pivot_table(index="country", columns="Year", values="ships", aggfunc="sum").reset_index()
        country_rows = []
        for c in piv_fob["country"].unique():
            c_fob  = safe_float(safe_pivot_val(piv_fob,"country",c,cy))
            p_fob  = safe_float(safe_pivot_val(piv_fob,"country",c,py))
            p2_fob = safe_float(safe_pivot_val(piv_fob,"country",c,p2y))
            c_shp  = safe_int(safe_pivot_val(piv_shp,"country",c,cy))
            p_shp  = safe_int(safe_pivot_val(piv_shp,"country",c,py))
            p2_shp = safe_int(safe_pivot_val(piv_shp,"country",c,p2y))
            chg_py = pct_change(c_fob,p_fob)
            chg_p2 = pct_change(c_fob,p2_fob)
            badge  = status_badge(chg_py,c_fob)
            country_rows.append({
                "Country":     f"{flag(c)} {c}",
                f"Ships {cy}": c_shp, f"Ships {py}": p_shp or "—", f"Ships {p2y}": p2_shp or "—",
                f"FOB {cy}":   f"$ {c_fob:,.0f}",
                f"FOB {py}":   f"$ {p_fob:,.0f}"  if p_fob  else "—",
                f"FOB {p2y}":  f"$ {p2_fob:,.0f}" if p2_fob else "—",
                f"vs {py}":    f"{chg_py:+.1f}%"   if chg_py is not None else "—",
                f"vs {p2y}":   f"{chg_p2:+.1f}%"   if chg_p2 is not None else "—",
                "Status":      badge,
            })
        country_rows.sort(key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")), reverse=True)
        st.dataframe(pd.DataFrame(country_rows), use_container_width=True, hide_index=True)

        divider()
        section_label(f"Customer Performance by Country  ·  {scope_lbl}")
        info_strip("Each country panel shows every customer active in any selected year. Status compares current-year FOB vs prior year.", "#8C3D3D")
        ccy = dff.groupby(["country","customer_name","delivery_year"]).agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique"), units=("total_quantity","sum")).reset_index()
        top_cntry = ccy[ccy["delivery_year"]==cur_year].groupby("country")["fob"].sum().sort_values(ascending=False).index.tolist()
        for country in top_cntry + [c for c in ccy["country"].unique() if c not in top_cntry]:
            cdf_c = ccy[ccy["country"]==country]
            if cdf_c.empty: continue
            tot_fob = safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
            tot_shp = safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())
            with st.expander(f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f}  ({scope_lbl} {cur_year})", expanded=False):
                piv_c_fob  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="fob",   aggfunc="sum").reset_index()
                piv_c_shp  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="ships", aggfunc="sum").reset_index()
                piv_c_unit = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="units", aggfunc="sum").reset_index()
                cust_rows = []
                for _, r in piv_c_fob.iterrows():
                    cname  = r["customer_name"]
                    cf     = safe_float(r.get(cur_year,   0))
                    pf     = safe_float(r.get(prev_year,  0))
                    p2f    = safe_float(r.get(prev2_year, 0))
                    cs     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, cur_year))
                    ps     = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, prev_year))
                    cu     = safe_int(safe_pivot_val(piv_c_unit, "customer_name", cname, cur_year))
                    chg    = pct_change(cf, pf)
                    chg2   = pct_change(cf, p2f)
                    cbadge = status_badge(chg, cf)
                    cust_rows.append({
                        "Customer": cname, f"FOB {cy}": f"$ {cf:,.0f}",
                        f"FOB {py}": f"$ {pf:,.0f}" if pf else "—",
                        f"FOB {p2y}": f"$ {p2f:,.0f}" if p2f else "—",
                        f"vs {py}": f"{chg:+.1f}%" if chg is not None else "—",
                        f"vs {p2y}": f"{chg2:+.1f}%" if chg2 is not None else "—",
                        f"Ships {cy}": cs, f"Ships {py}": ps or "—",
                        f"Units {cy}": f"{cu:,}", "Status": cbadge,
                    })
                cust_rows.sort(key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","")), reverse=True)
                if cust_rows:
                    st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)
                    cdf_cur = cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob", ascending=False).head(12)
                    if not cdf_cur.empty:
                        fig_mini = px.bar(cdf_cur, x="customer_name", y="fob",
                                          labels={"customer_name":"","fob":"FOB (USD)"},
                                          color_discrete_sequence=["#8C3D3D"])
                        fig_mini.update_yaxes(tickprefix="$ ")
                        fig_mini.update_xaxes(tickangle=-30)
                        plotly_layout(fig_mini, height=200)
                        st.plotly_chart(fig_mini, use_container_width=True)

        divider()
        section_label("Growth Opportunity Focus")
        decline = [r for r in country_rows if any(k in r["Status"] for k in ["Declining","At risk","Lost"])]
        growing = [r for r in country_rows if any(k in r["Status"] for k in ["Growing","Strong"])]
        new_mkt = [r for r in country_rows if "New" in r["Status"]]
        g1,g2,g3 = st.columns(3)
        def focus_col(col, title, color, items):
            col.markdown(f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;text-transform:uppercase;color:{color};margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid {color};">{title}</div>', unsafe_allow_html=True)
            if not items:
                col.markdown('<div style="font-family:Jost,sans-serif;font-size:.82rem;color:#7A7A7A;padding:6px 0;">None</div>', unsafe_allow_html=True)
            for r in items:
                chg = r.get(f"vs {py}","—")
                col.markdown(f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #EDE9E3;"><span style="font-family:Jost,sans-serif;font-size:.82rem;color:#1A1A1A;">{r["Country"]}</span><span style="font-family:Jost,sans-serif;font-size:.75rem;font-weight:500;color:{color};">{chg}</span></div>', unsafe_allow_html=True)
        focus_col(g1,"Needs attention","#8C3D3D",decline)
        focus_col(g2,"Growing markets","#2D4A3E",growing)
        focus_col(g3,"New markets","#B8924A",new_mkt)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — GROWTH TARGETS
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[1]:
        section_label(f"Growth Targets  ·  {cur_year}  ·  {scope_lbl}", "#8C3D3D")
        info_strip("Set a target FOB growth % for the current year. The dashboard calculates where you need to be each week to hit it and shows your current gap.", "#2D4A3E")

        tg1, tg2 = st.columns([1, 3])
        target_pct = tg1.number_input("Global FOB growth target (%)", min_value=0.0, max_value=200.0, value=10.0, step=0.5, key="target_pct")
        target_fob = prev_fob * (1 + target_pct / 100) if prev_fob > 0 else 0.0

        if target_fob > 0:
            gap       = target_fob - cur_fob
            pace_pct  = (cur_fob / target_fob * 100) if target_fob else 0
            on_track  = cur_fob >= (prev_fob * (1 + target_pct/100) * (current_week / 52))

            with tg2:
                info_strip(
                    f"Target FOB for {cur_year}: <strong>$ {target_fob:,.0f}</strong>  "
                    f"({target_pct:+.1f}% vs {prev_year})<br>"
                    f"Current FOB: <strong>$ {cur_fob:,.0f}</strong>  ·  "
                    f"Gap to target: <strong style='color:{'#2D4A3E' if gap<=0 else '#8C3D3D'};'>"
                    f"{'$ {:,.0f} ahead'.format(-gap) if gap<=0 else '$ {:,.0f} behind'.format(gap)}</strong>",
                    "#2D4A3E" if gap <= 0 else "#8C3D3D")

            k1,k2,k3,k4 = st.columns(4)
            k1.metric("Target FOB",     f"$ {target_fob:,.0f}")
            k2.metric("Achieved",       f"$ {cur_fob:,.0f}",  delta=f"{pace_pct-100:+.1f}% of target")
            k3.metric("Gap",            f"$ {abs(gap):,.0f}",  delta="ahead" if gap<=0 else "behind")
            k4.metric("Pace",           f"{'On track ✓' if on_track else 'Behind pace'}")

            divider()

            # Weekly pace chart — actual vs required pace line
            section_label("Weekly Pace  ·  Actual vs Required")
            wk_actual = dff[dff["delivery_year"].isin([cur_year, prev_year])].groupby(
                ["delivery_year","delivery_week"]).agg(fob=("total_price","sum")).reset_index()

            cur_wk  = wk_actual[wk_actual["delivery_year"]==cur_year].sort_values("delivery_week")
            prev_wk = wk_actual[wk_actual["delivery_year"]==prev_year].sort_values("delivery_week") if prev_year in wk_actual["delivery_year"].values else pd.DataFrame()

            cur_wk  = cur_wk.copy();  cur_wk["cumulative"]  = cur_wk["fob"].cumsum()
            if not prev_wk.empty:
                prev_wk = prev_wk.copy(); prev_wk["cumulative"] = prev_wk["fob"].cumsum()

            all_weeks = list(range(1, (current_week if use_ytd else 53)))
            target_line = [target_fob * (w / (current_week if use_ytd else 52)) for w in all_weeks]

            fig_pace = go.Figure()
            fig_pace.add_trace(go.Scatter(
                x=cur_wk["delivery_week"], y=cur_wk["cumulative"],
                name=f"{cur_year} Actual", line=dict(color="#8C3D3D", width=2.5), mode="lines+markers", marker_size=4))
            if not prev_wk.empty:
                fig_pace.add_trace(go.Scatter(
                    x=prev_wk["delivery_week"], y=prev_wk["cumulative"],
                    name=f"{prev_year} Actual", line=dict(color="#B8924A", width=1.5, dash="dot"), mode="lines"))
            fig_pace.add_trace(go.Scatter(
                x=all_weeks, y=target_line,
                name=f"Target pace ({target_pct:+.0f}%)",
                line=dict(color="#2D4A3E", width=1.5, dash="dash"), mode="lines"))
            fig_pace.update_yaxes(tickprefix="$ ")
            fig_pace.update_xaxes(title="ISO Week")
            plotly_layout(fig_pace, height=340)
            st.plotly_chart(fig_pace, use_container_width=True)

            divider()

            # Country-level target tracking
            section_label("Country-Level Target Tracking")
            cntry_cur  = cur_df.groupby("country").agg(fob_cur=("total_price","sum")).reset_index()
            cntry_prev = prev_df.groupby("country").agg(fob_prev=("total_price","sum")).reset_index() if not prev_df.empty else pd.DataFrame(columns=["country","fob_prev"])
            cntry_tgt  = cntry_cur.merge(cntry_prev, on="country", how="outer").fillna(0)
            cntry_tgt["target"]   = cntry_tgt["fob_prev"] * (1 + target_pct/100)
            cntry_tgt["gap"]      = cntry_tgt["target"] - cntry_tgt["fob_cur"]
            cntry_tgt["pct_done"] = np.where(cntry_tgt["target"]>0, cntry_tgt["fob_cur"]/cntry_tgt["target"]*100, 0)
            cntry_tgt["Country"]  = cntry_tgt["country"].apply(lambda c: f"{flag(c)} {c}")
            cntry_tgt = cntry_tgt.sort_values("fob_cur", ascending=False)

            tgt_rows = []
            for _, r in cntry_tgt.iterrows():
                tgt_rows.append({
                    "Country":          r["Country"],
                    f"FOB {cy}":        f"$ {safe_float(r['fob_cur']):,.0f}",
                    f"FOB {py}":        f"$ {safe_float(r['fob_prev']):,.0f}" if safe_float(r['fob_prev']) else "—",
                    f"Target ({target_pct:+.0f}%)": f"$ {safe_float(r['target']):,.0f}" if safe_float(r['target']) else "—",
                    "Gap":              f"$ {safe_float(r['gap']):,.0f}" if safe_float(r['gap'])>0 else f"✓ $ {abs(safe_float(r['gap'])):,.0f} ahead",
                    "% of Target":      f"{safe_float(r['pct_done']):.1f}%",
                })
            st.dataframe(pd.DataFrame(tgt_rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"No data for {prev_year} — targets require at least one prior year of data.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — CUSTOMER INTELLIGENCE
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[2]:
        section_label("Customer Concentration & Dependency Risk", "#8C3D3D")
        info_strip("High concentration in few customers = high revenue risk. A healthy portfolio spreads revenue across many accounts.", "#8C3D3D")

        cust_fob = cur_df.groupby("customer_name").agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique"),
            units=("total_quantity","sum"), countries=("country","nunique")).reset_index()
        cust_fob = cust_fob.sort_values("fob", ascending=False).reset_index(drop=True)
        total_fob_cur = safe_float(cust_fob["fob"].sum())
        cust_fob["share_%"]   = cust_fob["fob"] / total_fob_cur * 100 if total_fob_cur else 0
        cust_fob["cumulative_%"] = cust_fob["share_%"].cumsum()

        # How many customers = 80% of revenue?
        top80 = (cust_fob["cumulative_%"] <= 80).sum() + 1
        info_strip(f"<strong>{top80} customer{'s' if top80!=1 else ''}</strong> account for 80% of your current FOB. "
                   f"Total active customers this period: <strong>{len(cust_fob)}</strong>.", "#4A6080")

        fig_conc = px.bar(cust_fob.head(20), x="customer_name", y="fob",
                          labels={"customer_name":"Customer","fob":"FOB (USD)"},
                          color="share_%", color_continuous_scale=["#F0EAE2","#8C3D3D"])
        fig_conc.update_yaxes(tickprefix="$ ")
        fig_conc.update_xaxes(tickangle=-35)
        fig_conc.update_coloraxes(colorbar_title="Share %")
        plotly_layout(fig_conc, height=320)
        st.plotly_chart(fig_conc, use_container_width=True)

        divider()
        section_label("Top Growing & Declining Customers", "#2D4A3E")

        if not prev_df.empty:
            cust_prev = prev_df.groupby("customer_name").agg(fob_prev=("total_price","sum")).reset_index()
            cust_comp = cust_fob[["customer_name","fob"]].merge(cust_prev, on="customer_name", how="outer").fillna(0)
            cust_comp["chg_pct"] = cust_comp.apply(lambda r: pct_change(r["fob"], r["fob_prev"]), axis=1)
            cust_comp = cust_comp[cust_comp["fob"] > 0].dropna(subset=["chg_pct"])
            cust_comp = cust_comp.sort_values("chg_pct", ascending=False)

            top5   = cust_comp.head(5)
            bot5   = cust_comp.tail(5).sort_values("chg_pct")

            col_g, col_d = st.columns(2)
            with col_g:
                st.markdown('<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#2D4A3E;margin-bottom:8px;border-bottom:2px solid #2D4A3E;padding-bottom:6px;">Top 5 Growing</div>', unsafe_allow_html=True)
                for _, r in top5.iterrows():
                    st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #EDE9E3;"><span style="font-size:.84rem;color:#1A1A1A;">{r["customer_name"]}</span><span style="font-size:.82rem;font-weight:500;color:#2D4A3E;">{r["chg_pct"]:+.1f}%  ·  $ {safe_float(r["fob"]):,.0f}</span></div>', unsafe_allow_html=True)
            with col_d:
                st.markdown('<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.14em;text-transform:uppercase;color:#8C3D3D;margin-bottom:8px;border-bottom:2px solid #8C3D3D;padding-bottom:6px;">Top 5 Declining</div>', unsafe_allow_html=True)
                for _, r in bot5.iterrows():
                    st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #EDE9E3;"><span style="font-size:.84rem;color:#1A1A1A;">{r["customer_name"]}</span><span style="font-size:.82rem;font-weight:500;color:#8C3D3D;">{r["chg_pct"]:+.1f}%  ·  $ {safe_float(r["fob"]):,.0f}</span></div>', unsafe_allow_html=True)
        else:
            st.info("Need prior-year data to show growth/decline rankings.")

        divider()
        section_label("New Customer Tracking", "#B8924A")
        info_strip("Customers with no activity in prior years — tracked from their first order week.", "#B8924A")

        all_prev = dff[dff["delivery_year"] < cur_year]["customer_name"].unique()
        new_custs = cur_df[~cur_df["customer_name"].isin(all_prev)]

        if not new_custs.empty:
            nc_grp = new_custs.groupby("customer_name").agg(
                first_week=("delivery_week","min"),
                weeks_active=("delivery_week","nunique"),
                fob=("total_price","sum"),
                ships=("shipment_id","nunique"),
                countries=("country", lambda x: ", ".join(sorted(x.unique())))).reset_index()
            nc_grp = nc_grp.sort_values("fob", ascending=False)
            nc_grp["FOB"] = nc_grp["fob"].apply(lambda x: f"$ {x:,.0f}")
            st.dataframe(nc_grp[["customer_name","first_week","weeks_active","ships","FOB","countries"]].rename(columns={
                "customer_name":"Customer","first_week":"First Week","weeks_active":"Active Weeks",
                "ships":"Shipments","countries":"Countries"}),
                use_container_width=True, hide_index=True)
        else:
            st.info(f"No new customers in {cur_year} compared to prior years.")

        divider()
        section_label(f"Weekly Run-Rate  ·  {cur_year} vs {prev_year}", "#4A6080")
        info_strip("Compare each individual week this year vs the same week last year — spot exactly which weeks are ahead or behind.", "#4A6080")

        if not prev_df.empty:
            wk_cur  = cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_prev = prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_rr   = wk_cur.merge(wk_prev, on="delivery_week", how="outer").fillna(0)
            wk_rr   = wk_rr.sort_values("delivery_week")
            wk_rr["diff"]   = wk_rr["fob_cur"] - wk_rr["fob_prev"]
            wk_rr["color"]  = wk_rr["diff"].apply(lambda x: "#2D4A3E" if x >= 0 else "#8C3D3D")

            fig_rr = go.Figure()
            fig_rr.add_bar(x=wk_rr["delivery_week"], y=wk_rr["fob_prev"],
                           name=f"{prev_year}", marker_color="#DDD8D0")
            fig_rr.add_bar(x=wk_rr["delivery_week"], y=wk_rr["fob_cur"],
                           name=f"{cur_year}", marker_color="#8C3D3D")
            fig_rr.update_layout(barmode="overlay", bargroupgap=0.1)
            fig_rr.update_yaxes(tickprefix="$ ")
            fig_rr.update_xaxes(title="ISO Week")
            plotly_layout(fig_rr, height=300)
            st.plotly_chart(fig_rr, use_container_width=True)

            wk_rr["Week"]       = wk_rr["delivery_week"].apply(lambda w: f"W{int(w)}")
            wk_rr[f"FOB {cy}"]  = wk_rr["fob_cur"].apply(lambda x: f"$ {x:,.0f}")
            wk_rr[f"FOB {py}"]  = wk_rr["fob_prev"].apply(lambda x: f"$ {x:,.0f}")
            wk_rr["Difference"] = wk_rr["diff"].apply(lambda x: f"{'▲' if x>=0 else '▼'} $ {abs(x):,.0f}")
            st.dataframe(wk_rr[["Week", f"FOB {cy}", f"FOB {py}", "Difference"]], use_container_width=True, hide_index=True)
        else:
            st.info(f"No {prev_year} data available for run-rate comparison.")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — PRODUCT MIX
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[3]:
        section_label(f"Product Mix Analysis  ·  {scope_lbl}  ·  {cur_year}", "#2D4A3E")
        info_strip("Understand which crops and varieties drive your FOB — and how the mix has shifted vs prior year.", "#2D4A3E")

        has_crop = "crop_name" in cur_df.columns and cur_df["crop_name"].astype(str).str.strip().ne("").any()
        has_var  = "variety_name" in cur_df.columns and cur_df["variety_name"].astype(str).str.strip().ne("").any()

        if has_crop:
            crop_grp = cur_df[cur_df["crop_name"].astype(str).str.strip()!=""].groupby("crop_name").agg(
                fob=("total_price","sum"), units=("total_quantity","sum"),
                customers=("customer_name","nunique"), countries=("country","nunique")).reset_index()
            crop_grp = crop_grp.sort_values("fob", ascending=False)
            total_crop_fob = safe_float(crop_grp["fob"].sum())
            crop_grp["share_%"] = crop_grp["fob"] / total_crop_fob * 100 if total_crop_fob else 0

            col_pie, col_bar = st.columns(2)
            with col_pie:
                fig_pie = px.pie(crop_grp, names="crop_name", values="fob",
                                 color_discrete_sequence=PALETTE,
                                 hole=0.45)
                fig_pie.update_traces(textposition="outside", textinfo="label+percent")
                fig_pie.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0),
                                      paper_bgcolor="rgba(0,0,0,0)", font_family="Jost",
                                      font_color="#1A1A1A", height=300)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_bar:
                fig_crop = px.bar(crop_grp, x="crop_name", y="fob",
                                  color="share_%", color_continuous_scale=["#F0EAE2","#8C3D3D"],
                                  labels={"crop_name":"Crop","fob":"FOB (USD)"})
                fig_crop.update_yaxes(tickprefix="$ ")
                fig_crop.update_coloraxes(showscale=False)
                plotly_layout(fig_crop, height=300)
                st.plotly_chart(fig_crop, use_container_width=True)

            # YoY crop comparison
            if not prev_df.empty and has_crop:
                divider()
                section_label(f"Crop Mix Shift  ·  {cur_year} vs {prev_year}")
                crop_prev = prev_df[prev_df["crop_name"].astype(str).str.strip()!=""].groupby("crop_name").agg(fob_prev=("total_price","sum")).reset_index()
                crop_comp = crop_grp[["crop_name","fob"]].merge(crop_prev, on="crop_name", how="outer").fillna(0)
                crop_comp["chg"] = crop_comp.apply(lambda r: pct_change(r["fob"], r["fob_prev"]), axis=1)
                crop_comp = crop_comp.sort_values("fob", ascending=False)
                crop_comp[f"FOB {cy}"]  = crop_comp["fob"].apply(lambda x: f"$ {x:,.0f}")
                crop_comp[f"FOB {py}"]  = crop_comp["fob_prev"].apply(lambda x: f"$ {x:,.0f}" if x else "—")
                crop_comp["Change"]     = crop_comp["chg"].apply(lambda x: f"{x:+.1f}%" if x is not None else "—")
                st.dataframe(crop_comp[["crop_name",f"FOB {cy}",f"FOB {py}","Change"]].rename(columns={"crop_name":"Crop"}), use_container_width=True, hide_index=True)
        else:
            st.info("No crop data found. Ensure the `crop_name` column is populated.")

        if has_var:
            divider()
            section_label(f"Top Varieties by FOB  ·  {cur_year}")
            var_grp = cur_df[cur_df["variety_name"].astype(str).str.strip()!=""].groupby(["crop_name","variety_name"]).agg(
                fob=("total_price","sum"), units=("total_quantity","sum"),
                customers=("customer_name","nunique")).reset_index()
            var_grp = var_grp.sort_values("fob", ascending=False).head(25)
            var_grp["label"] = var_grp["variety_name"] + " (" + var_grp["crop_name"] + ")"
            fig_var = px.bar(var_grp, x="fob", y="label", orientation="h",
                             labels={"fob":"FOB (USD)","label":""},
                             color_discrete_sequence=["#2D4A3E"])
            fig_var.update_xaxes(tickprefix="$ ")
            fig_var.update_layout(yaxis=dict(autorange="reversed"))
            plotly_layout(fig_var, height=max(300, len(var_grp)*26))
            st.plotly_chart(fig_var, use_container_width=True)

            # Customer × variety
            divider()
            section_label("Product Mix per Customer  ·  Top 15 Customers")
            top_custs = cur_df.groupby("customer_name")["total_price"].sum().nlargest(15).index.tolist()
            cust_var = cur_df[cur_df["customer_name"].isin(top_custs) & cur_df["variety_name"].astype(str).str.strip().ne("")].groupby(
                ["customer_name","variety_name"]).agg(fob=("total_price","sum")).reset_index()
            if not cust_var.empty:
                fig_cv = px.bar(cust_var, x="customer_name", y="fob", color="variety_name",
                                labels={"customer_name":"Customer","fob":"FOB (USD)","variety_name":"Variety"},
                                color_discrete_sequence=PALETTE)
                fig_cv.update_yaxes(tickprefix="$ ")
                fig_cv.update_xaxes(tickangle=-35)
                plotly_layout(fig_cv, height=380)
                st.plotly_chart(fig_cv, use_container_width=True)

        if not has_crop and not has_var:
            st.info("No crop or variety data found in the dataset.")

        divider()
        section_label(f"FOB per Unit Trend  ·  Price Realisation")
        info_strip("Are we growing FOB through volume, price, or both? A rising FOB/unit means better price realisation; flat or falling means growth is purely volume.", "#4A6080")

        fpu = dff.groupby("delivery_year").agg(fob=("total_price","sum"), units=("total_quantity","sum")).reset_index()
        fpu["fob_per_unit"] = fpu.apply(lambda r: safe_float(r["fob"]) / safe_float(r["units"]) if safe_float(r["units"]) > 0 else 0, axis=1)
        fpu["Year"] = fpu["delivery_year"].astype(str)
        col_v, col_p = st.columns(2)
        with col_v:
            fig_vol = px.bar(fpu, x="Year", y="units", labels={"units":"Units Shipped","Year":""},
                             color_discrete_sequence=["#B8924A"])
            plotly_layout(fig_vol, height=240)
            st.plotly_chart(fig_vol, use_container_width=True)
        with col_p:
            fig_fpu = px.bar(fpu, x="Year", y="fob_per_unit", labels={"fob_per_unit":"FOB / Unit (USD)","Year":""},
                             color_discrete_sequence=["#2D4A3E"])
            fig_fpu.update_yaxes(tickprefix="$ ")
            plotly_layout(fig_fpu, height=240)
            st.plotly_chart(fig_fpu, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 5 — SEASONALITY
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[4]:
        section_label(f"Seasonality Heatmap  ·  FOB by Week  ·  {cur_year}", "#4A6080")
        info_strip("Which weeks are your strongest? Use this to plan inventory, staffing, and commercial push timing.", "#4A6080")

        # Country × Week heatmap
        season = cur_df.groupby(["country","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        if not season.empty:
            heat_piv = season.pivot_table(index="country", columns="delivery_week", values="fob", aggfunc="sum").fillna(0)
            top_countries = heat_piv.sum(axis=1).nlargest(15).index
            heat_piv = heat_piv.loc[top_countries]

            fig_sea = go.Figure(data=go.Heatmap(
                z=heat_piv.values,
                x=[f"W{int(w)}" for w in heat_piv.columns],
                y=heat_piv.index.tolist(),
                colorscale=[[0,"#F5F2ED"],[0.3,"#F0EAE2"],[0.6,"#C47A7A"],[1,"#5C1F1F"]],
                hoverongaps=False,
                hovertemplate="Country: %{y}<br>Week: %{x}<br>FOB: $ %{z:,.0f}<extra></extra>",
            ))
            fig_sea.update_layout(
                plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                font_family="Jost", font_color="#1A1A1A",
                margin=dict(l=0,r=0,t=16,b=0),
                height=max(300, len(top_countries)*32),
                xaxis=dict(side="top", tickfont=dict(size=10, color="#4A4A4A")),
                yaxis=dict(tickfont=dict(size=11, color="#1A1A1A")),
            )
            st.plotly_chart(fig_sea, use_container_width=True)

        divider()
        section_label(f"Strongest Weeks by FOB  ·  {cur_year}")
        wk_total = cur_df.groupby("delivery_week").agg(fob=("total_price","sum"), ships=("shipment_id","nunique"), customers=("customer_name","nunique")).reset_index()
        wk_total = wk_total.sort_values("fob", ascending=False).head(10)
        wk_total["Week"]       = wk_total["delivery_week"].apply(lambda w: week_label(cur_year, int(w)))
        wk_total["FOB"]        = wk_total["fob"].apply(lambda x: f"$ {x:,.0f}")
        wk_total["Shipments"]  = wk_total["ships"]
        wk_total["Customers"]  = wk_total["customers"]
        st.dataframe(wk_total[["Week","FOB","Shipments","Customers"]], use_container_width=True, hide_index=True)

        if not prev_df.empty:
            divider()
            section_label(f"Week-by-Week Comparison  ·  {cur_year} vs {prev_year}")
            wk_sea_prev = prev_df.groupby("delivery_week").agg(fob_prev=("total_price","sum")).reset_index()
            wk_sea_cur  = cur_df.groupby("delivery_week").agg(fob_cur=("total_price","sum")).reset_index()
            wk_sea_mrg  = wk_sea_cur.merge(wk_sea_prev, on="delivery_week", how="outer").fillna(0).sort_values("delivery_week")
            fig_wk = go.Figure()
            fig_wk.add_trace(go.Scatter(x=wk_sea_mrg["delivery_week"], y=wk_sea_mrg["fob_prev"],
                                        name=str(prev_year), line=dict(color="#DDD8D0", width=2), mode="lines"))
            fig_wk.add_trace(go.Scatter(x=wk_sea_mrg["delivery_week"], y=wk_sea_mrg["fob_cur"],
                                        name=str(cur_year), line=dict(color="#8C3D3D", width=2.5), mode="lines+markers", marker_size=4))
            fig_wk.update_yaxes(tickprefix="$ ")
            fig_wk.update_xaxes(title="ISO Week")
            plotly_layout(fig_wk, height=300)
            st.plotly_chart(fig_wk, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 6 — ORIGIN MIX
    # ════════════════════════════════════════════════════════════════════════
    with ci_tabs[5]:
        section_label(f"Origin Mix Analysis  ·  {scope_lbl}  ·  {cur_year}", "#B8924A")
        info_strip("Which supply origins feed which destination markets? Use this to spot over-reliance on a single source and identify diversification opportunities.", "#B8924A")

        orig_grp = cur_df.groupby("supply_source_name").agg(
            fob=("total_price","sum"), ships=("shipment_id","nunique"),
            units=("total_quantity","sum"), countries=("country","nunique"),
            customers=("customer_name","nunique")).reset_index()
        orig_grp = orig_grp.sort_values("fob", ascending=False)
        total_orig_fob = safe_float(orig_grp["fob"].sum())
        orig_grp["share_%"] = orig_grp["fob"] / total_orig_fob * 100 if total_orig_fob else 0

        oc1, oc2 = st.columns(2)
        with oc1:
            fig_opie = px.pie(orig_grp, names="supply_source_name", values="fob",
                              color_discrete_sequence=PALETTE, hole=0.45,
                              labels={"supply_source_name":"Origin"})
            fig_opie.update_traces(textposition="outside", textinfo="label+percent")
            fig_opie.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0),
                                   paper_bgcolor="rgba(0,0,0,0)", font_family="Jost",
                                   font_color="#1A1A1A", height=300)
            st.plotly_chart(fig_opie, use_container_width=True)
        with oc2:
            orig_grp_disp = orig_grp.copy()
            orig_grp_disp["FOB"]       = orig_grp_disp["fob"].apply(lambda x: f"$ {x:,.0f}")
            orig_grp_disp["Share"]     = orig_grp_disp["share_%"].apply(lambda x: f"{x:.1f}%")
            orig_grp_disp["Shipments"] = orig_grp_disp["ships"]
            orig_grp_disp["Countries"] = orig_grp_disp["countries"]
            orig_grp_disp["Customers"] = orig_grp_disp["customers"]
            st.dataframe(orig_grp_disp[["supply_source_name","FOB","Share","Shipments","Countries","Customers"]].rename(
                columns={"supply_source_name":"Origin"}), use_container_width=True, hide_index=True)

        divider()
        section_label("Origin → Destination Flow")
        orig_dest = cur_df.groupby(["supply_source_name","country"]).agg(fob=("total_price","sum")).reset_index()
        orig_dest = orig_dest[orig_dest["fob"] > 0]
        if not orig_dest.empty:
            fig_od = px.bar(orig_dest, x="country", y="fob", color="supply_source_name",
                            barmode="stack",
                            labels={"country":"Destination","fob":"FOB (USD)","supply_source_name":"Origin"},
                            color_discrete_sequence=PALETTE)
            fig_od.update_yaxes(tickprefix="$ ")
            fig_od.update_xaxes(tickangle=-35)
            plotly_layout(fig_od, height=380)
            st.plotly_chart(fig_od, use_container_width=True)

        divider()
        section_label("Origin YoY Comparison")
        if not prev_df.empty:
            orig_prev = prev_df.groupby("supply_source_name").agg(fob_prev=("total_price","sum")).reset_index()
            orig_comp = orig_grp[["supply_source_name","fob"]].merge(orig_prev, on="supply_source_name", how="outer").fillna(0)
            orig_comp["chg"] = orig_comp.apply(lambda r: pct_change(r["fob"], r["fob_prev"]), axis=1)
            orig_comp = orig_comp.sort_values("fob", ascending=False)
            orig_comp[f"FOB {cy}"]  = orig_comp["fob"].apply(lambda x: f"$ {x:,.0f}")
            orig_comp[f"FOB {py}"]  = orig_comp["fob_prev"].apply(lambda x: f"$ {x:,.0f}" if x else "—")
            orig_comp["Change"]     = orig_comp["chg"].apply(lambda x: f"{x:+.1f}%" if x is not None else "—")
            orig_comp["Status"]     = orig_comp.apply(lambda r: status_badge(r["chg"], r["fob"]), axis=1)
            st.dataframe(orig_comp[["supply_source_name",f"FOB {cy}",f"FOB {py}","Change","Status"]].rename(
                columns={"supply_source_name":"Origin"}), use_container_width=True, hide_index=True)
        else:
            st.info(f"No {prev_year} data for origin comparison.")

        divider()
        section_label("Weekly Origin Activity  ·  Heatmap")
        orig_wk = cur_df.groupby(["supply_source_name","delivery_week"]).agg(fob=("total_price","sum")).reset_index()
        if not orig_wk.empty:
            orig_heat = orig_wk.pivot_table(index="supply_source_name", columns="delivery_week", values="fob", aggfunc="sum").fillna(0)
            fig_oh = go.Figure(data=go.Heatmap(
                z=orig_heat.values,
                x=[f"W{int(w)}" for w in orig_heat.columns],
                y=orig_heat.index.tolist(),
                colorscale=[[0,"#F5F2ED"],[0.3,"#D4B070"],[1,"#5C2D00"]],
                hoverongaps=False,
                hovertemplate="Origin: %{y}<br>Week: %{x}<br>FOB: $ %{z:,.0f}<extra></extra>",
            ))
            fig_oh.update_layout(
                plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                font_family="Jost", font_color="#1A1A1A",
                margin=dict(l=0,r=0,t=16,b=0),
                height=max(200, len(orig_heat)*40),
                xaxis=dict(side="top", tickfont=dict(size=10, color="#4A4A4A")),
                yaxis=dict(tickfont=dict(size=11, color="#1A1A1A")),
            )
            st.plotly_chart(fig_oh, use_container_width=True)

    return  # end render_commercial

    page_header("Commercial Intelligence",
                "Year-over-Year Performance  ·  Growth Analysis  ·  Market Focus")

    # ── Scope ──────────────────────────────────────────────────────────────
    today_iso    = date.today().isocalendar()
    current_week = today_iso[1]

    col_scope, col_note = st.columns([1, 2])
    with col_scope:
        scope = st.radio("Comparison scope", [
            "📅  Year-to-Date",
            "📆  Full Year"
        ], key="ci_scope")
    with col_note:
        use_ytd = "Year-to-Date" in scope
        if use_ytd:
            info_strip(
                f"Comparing <strong>Week 1 – Week {current_week}</strong> across all years. "
                f"Prior years are capped at week {current_week} for a fair, apples-to-apples comparison.",
                "#2D4A3E")
        else:
            info_strip(
                "Comparing <strong>all weeks present in the system</strong> per year — "
                "including future confirmed orders. Useful for full-year forecasting.",
                "#B8924A")

    divider()

    # ── Filters ──────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    default_years = years_avail[-3:] if len(years_avail) >= 3 else years_avail
    sel_years     = fc1.multiselect("Years", years_avail, default=default_years, key="ci_years")
    sel_customers = fc2.multiselect("Customers", all_customers, default=[], key="ci_customers", placeholder="All customers")
    sel_countries = fc3.multiselect("Destination countries", all_countries, default=[], key="ci_countries", placeholder="All countries")

    if not sel_years:
        st.warning("Select at least one year.")
        return

    dff = df[df["delivery_year"].isin(sel_years)].copy()
    if sel_customers: dff = dff[dff["customer_name"].isin(sel_customers)]
    if sel_countries: dff = dff[dff["country"].isin(sel_countries)]
    # Exclude transit/supply hubs — not end-customer markets
    dff = dff[~dff["country"].isin(EXCLUDED_COUNTRIES)].copy()
    if use_ytd:       dff = dff[dff["delivery_week"] <= current_week]

    if dff.empty:
        st.info("No data matches the selected filters.")
        return

    cur_year   = max(sel_years)
    prev_year  = cur_year - 1
    prev2_year = cur_year - 2
    cy, py, p2y = str(cur_year), str(prev_year), str(prev2_year)
    scope_lbl = f"YTD W1–W{current_week}" if use_ytd else "Full Year"

    cur_df   = dff[dff["delivery_year"]==cur_year]
    prev_df  = dff[dff["delivery_year"]==prev_year]  if prev_year  in dff["delivery_year"].values else pd.DataFrame()
    prev2_df = dff[dff["delivery_year"]==prev2_year] if prev2_year in dff["delivery_year"].values else pd.DataFrame()

    # ── KPIs ─────────────────────────────────────────────────────────────────
    section_label(f"Summary  ·  {scope_lbl}  ·  {cur_year} vs {prev_year}")

    cur_ship  = n_shipments(cur_df)
    prev_ship = n_shipments(prev_df)
    cur_fob   = safe_float(cur_df["total_price"].sum())
    prev_fob  = safe_float(prev_df["total_price"].sum()) if not prev_df.empty else 0.0
    cur_units = safe_float(cur_df["total_quantity"].sum())
    prev_units= safe_float(prev_df["total_quantity"].sum()) if not prev_df.empty else 0.0

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Shipments",        f"{cur_ship:,}",        delta=metric_delta_str(cur_ship,  prev_ship))
    k2.metric("FOB Value",        f"$ {cur_fob:,.0f}",    delta=metric_delta_str(cur_fob,   prev_fob))
    k3.metric("Units Shipped",    f"{int(cur_units):,}",  delta=metric_delta_str(cur_units, prev_units))
    k4.metric("Active Customers", f"{cur_df['customer_name'].nunique():,}")

    divider()

    # ── Weekly FOB trend ─────────────────────────────────────────────────────
    section_label(f"Weekly FOB Trend  ·  {scope_lbl}")

    weekly = (
        dff.groupby(["delivery_year","delivery_week"])
        .agg(fob=("total_price","sum"))
        .reset_index()
    )
    weekly["Year"] = weekly["delivery_year"].astype(str)

    fig_trend = px.line(
        weekly, x="delivery_week", y="fob", color="Year",
        labels={"delivery_week":"ISO Week","fob":"FOB (USD)","Year":"Year"},
        color_discrete_sequence=PALETTE, markers=True,
    )
    fig_trend.update_traces(line_width=2.5, marker_size=5)
    fig_trend.update_yaxes(tickprefix="$ ")
    plotly_layout(fig_trend, height=340)
    st.plotly_chart(fig_trend, use_container_width=True)

    divider()

    # ── FOB by Country ────────────────────────────────────────────────────────
    section_label(f"FOB by Destination Country  ·  Last 3 Years  ·  {scope_lbl}")

    cy_grp = (
        dff.groupby(["country","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"))
        .reset_index()
    )
    cy_grp["Year"]  = cy_grp["delivery_year"].astype(str)
    cy_grp["label"] = cy_grp["country"].apply(lambda c: f"{flag(c)} {c}")

    order = (cy_grp[cy_grp["Year"]==cy].sort_values("fob", ascending=False)["country"].tolist())
    others = [c for c in cy_grp["country"].unique() if c not in order]
    full_order = order + others
    cy_grp["sort_key"] = cy_grp["country"].apply(lambda c: full_order.index(c) if c in full_order else 999)
    cy_grp = cy_grp.sort_values("sort_key")

    fig_cntry = px.bar(
        cy_grp, x="label", y="fob", color="Year", barmode="group",
        labels={"label":"Country","fob":"FOB (USD)","Year":"Year"},
        color_discrete_sequence=PALETTE,
    )
    fig_cntry.update_yaxes(tickprefix="$ ")
    fig_cntry.update_xaxes(tickangle=-35)
    plotly_layout(fig_cntry, height=380)
    st.plotly_chart(fig_cntry, use_container_width=True)

    divider()

    # ── Country status table ──────────────────────────────────────────────────
    section_label(f"Country Status Table  ·  {scope_lbl}")

    piv_fob = cy_grp.pivot_table(index="country", columns="Year", values="fob",   aggfunc="sum").reset_index()
    piv_shp = cy_grp.pivot_table(index="country", columns="Year", values="ships", aggfunc="sum").reset_index()

    country_rows = []
    for c in piv_fob["country"].unique():
        c_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, cy))
        p_fob  = safe_float(safe_pivot_val(piv_fob, "country", c, py))
        p2_fob = safe_float(safe_pivot_val(piv_fob, "country", c, p2y))
        c_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, cy))
        p_shp  = safe_int(safe_pivot_val(piv_shp, "country", c, py))
        p2_shp = safe_int(safe_pivot_val(piv_shp, "country", c, p2y))
        chg_py = pct_change(c_fob, p_fob)
        chg_p2 = pct_change(c_fob, p2_fob)
        badge  = status_badge(chg_py, c_fob)
        country_rows.append({
            "Country":       f"{flag(c)} {c}",
            f"Ships {cy}":   c_shp,
            f"Ships {py}":   p_shp  or "—",
            f"Ships {p2y}":  p2_shp or "—",
            f"FOB {cy}":     f"$ {c_fob:,.0f}",
            f"FOB {py}":     f"$ {p_fob:,.0f}"  if p_fob  else "—",
            f"FOB {p2y}":    f"$ {p2_fob:,.0f}" if p2_fob else "—",
            f"vs {py}":      f"{chg_py:+.1f}%"  if chg_py is not None else "—",
            f"vs {p2y}":     f"{chg_p2:+.1f}%"  if chg_p2 is not None else "—",
            "Status":        badge,
        })

    country_rows.sort(
        key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","").strip()),
        reverse=True
    )
    st.dataframe(pd.DataFrame(country_rows), use_container_width=True, hide_index=True)

    divider()

    # ── Customer × Country ────────────────────────────────────────────────────
    section_label(f"Customer Performance by Country  ·  {scope_lbl}")
    info_strip(
        "Each country panel shows every customer active in any selected year. "
        "Status reflects current-year FOB vs prior year. "
        "Use this to identify where commercial focus is needed.",
        "#8C3D3D")

    ccy = (
        dff.groupby(["country","customer_name","delivery_year"])
        .agg(fob=("total_price","sum"), ships=("shipment_id","nunique"), units=("total_quantity","sum"))
        .reset_index()
    )

    top_cntry = (
        ccy[ccy["delivery_year"]==cur_year]
        .groupby("country")["fob"].sum()
        .sort_values(ascending=False).index.tolist()
    )
    other_c = [c for c in ccy["country"].unique() if c not in top_cntry]
    for country in (top_cntry + other_c):
        cdf_c = ccy[ccy["country"]==country]
        if cdf_c.empty: continue

        tot_fob = safe_float(cdf_c[cdf_c["delivery_year"]==cur_year]["fob"].sum())
        tot_shp = safe_int(cdf_c[cdf_c["delivery_year"]==cur_year]["ships"].sum())

        with st.expander(
            f"{flag(country)}  {country}   ·   {tot_shp} shipments   ·   $ {tot_fob:,.0f}  ({scope_lbl} {cur_year})",
            expanded=False
        ):
            piv_c_fob  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="fob",   aggfunc="sum").reset_index()
            piv_c_shp  = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="ships", aggfunc="sum").reset_index()
            piv_c_unit = cdf_c.pivot_table(index="customer_name", columns="delivery_year", values="units", aggfunc="sum").reset_index()

            cust_rows = []
            for _, r in piv_c_fob.iterrows():
                cname = r["customer_name"]
                cf    = safe_float(r.get(cur_year,   0))
                pf    = safe_float(r.get(prev_year,  0))
                p2f   = safe_float(r.get(prev2_year, 0))
                cs    = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, cur_year))
                ps    = safe_int(safe_pivot_val(piv_c_shp,  "customer_name", cname, prev_year))
                cu    = safe_int(safe_pivot_val(piv_c_unit, "customer_name", cname, cur_year))
                chg   = pct_change(cf, pf)
                chg2  = pct_change(cf, p2f)
                cbadge = status_badge(chg, cf)
                cust_rows.append({
                    "Customer":     cname,
                    f"FOB {cy}":    f"$ {cf:,.0f}",
                    f"FOB {py}":    f"$ {pf:,.0f}"  if pf  else "—",
                    f"FOB {p2y}":   f"$ {p2f:,.0f}" if p2f else "—",
                    f"vs {py}":     f"{chg:+.1f}%"   if chg  is not None else "—",
                    f"vs {p2y}":    f"{chg2:+.1f}%"  if chg2 is not None else "—",
                    f"Ships {cy}":  cs,
                    f"Ships {py}":  ps or "—",
                    f"Units {cy}":  f"{cu:,}",
                    "Status":       cbadge,
                })

            cust_rows.sort(
                key=lambda x: safe_float(str(x[f"FOB {cy}"]).replace("$","").replace(",","").strip()),
                reverse=True
            )

            if cust_rows:
                st.dataframe(pd.DataFrame(cust_rows), use_container_width=True, hide_index=True)

                cdf_cur = cdf_c[cdf_c["delivery_year"]==cur_year].sort_values("fob", ascending=False).head(12)
                if not cdf_cur.empty:
                    fig_mini = px.bar(
                        cdf_cur, x="customer_name", y="fob",
                        labels={"customer_name":"","fob":"FOB (USD)"},
                        color_discrete_sequence=["#8C3D3D"],
                    )
                    fig_mini.update_yaxes(tickprefix="$ ")
                    fig_mini.update_xaxes(tickangle=-30)
                    plotly_layout(fig_mini, height=200)
                    st.plotly_chart(fig_mini, use_container_width=True)

    divider()

    # ── Growth focus ──────────────────────────────────────────────────────────
    section_label("Growth Opportunity Focus")

    decline = [r for r in country_rows if any(k in r["Status"] for k in ["Declining","At risk","Lost"])]
    growing = [r for r in country_rows if any(k in r["Status"] for k in ["Growing","Strong"])]
    new_mkt = [r for r in country_rows if "New" in r["Status"]]

    g1, g2, g3 = st.columns(3)

    def focus_col(col, title, color, items):
        col.markdown(
            f'<div style="font-family:Jost,sans-serif;font-size:.65rem;letter-spacing:.16em;'
            f'text-transform:uppercase;color:{color};margin-bottom:10px;'
            f'padding-bottom:8px;border-bottom:2px solid {color};">{title}</div>',
            unsafe_allow_html=True)
        if not items:
            col.markdown('<div style="font-family:Jost,sans-serif;font-size:.82rem;color:#7A7A7A;padding:6px 0;">None</div>', unsafe_allow_html=True)
        for r in items:
            chg = r.get(f"vs {py}","—")
            col.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:7px 0;border-bottom:1px solid #EDE9E3;">'
                f'<span style="font-family:Jost,sans-serif;font-size:.82rem;color:#1A1A1A;">{r["Country"]}</span>'
                f'<span style="font-family:Jost,sans-serif;font-size:.75rem;font-weight:500;color:{color};">{chg}</span>'
                f'</div>',
                unsafe_allow_html=True)

    focus_col(g1, "Needs attention",  "#8C3D3D", decline)
    focus_col(g2, "Growing markets",  "#2D4A3E", growing)
    focus_col(g3, "New markets",      "#B8924A", new_mkt)


# ════════════════════════════════════════════════════════════════════════════
# LOGISTICS
# ════════════════════════════════════════════════════════════════════════════
def render_by_destination(df, accent, dl_key):
    if df.empty:
        st.info("No shipments found for this period.")
        return

    for country in sorted(df["country"].unique()):
        cdf  = df[df["country"]==country]
        n_s  = n_shipments(cdf)
        fob_t= safe_float(cdf["total_price"].sum())
        country_strip(country, n_s, fob_t, accent)

        for airport in sorted(cdf["iata_code"].dropna().unique()):
            adf    = cdf[cdf["iata_code"]==airport]
            n_sa   = n_shipments(adf)
            n_prod = len(adf)
            units  = safe_int(adf["total_quantity"].sum())
            fob_a  = safe_float(adf["total_price"].sum())

            with st.expander(
                f"✈  {airport}   {n_sa} shipment{'s' if n_sa!=1 else ''}  ·  "
                f"{n_prod} product line{'s' if n_prod!=1 else ''}  ·  "
                f"{units:,} units  ·  $ {fob_a:,.0f}",
                expanded=(n_s==1)
            ):
                for sid, sdf in adf.groupby("shipment_id", sort=False):
                    customer = sdf["customer_name"].iloc[0]
                    origin   = sdf["supply_source_name"].iloc[0]
                    shipment_row(customer, origin, len(sdf),
                                 safe_int(sdf["total_quantity"].sum()),
                                 safe_float(sdf["total_price"].sum()), accent)
                    line_cols = [c for c in ["crop_name","variety_name","product",
                                             "total_quantity","total_price","order_type"]
                                 if c in sdf.columns]
                    ldf = sdf[line_cols].copy()
                    ldf.columns = [c.replace("_"," ").title() for c in ldf.columns]
                    if "Total Price"    in ldf.columns: ldf["Total Price"]    = ldf["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                    if "Total Quantity" in ldf.columns: ldf["Total Quantity"] = ldf["Total Quantity"].apply(lambda x: f"{int(x):,}")
                    st.dataframe(ldf, use_container_width=True, hide_index=True)

    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    st.download_button("⬇  Export to Excel", data=buf.getvalue(),
        file_name="logistics_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"dl_{dl_key}")


def render_logistics(df_all):
    today    = date.today()
    iso      = today.isocalendar()
    cur_year, cur_week = iso[0], iso[1]

    VIEWS = [
        (-1,"Past Week",    "Quality Follow-up",   "#8C3D3D",
         "The logistics team must contact the customer to confirm receipt and quality. "
         "If negative feedback is received, contact the <strong>Sales Manager immediately</strong>."),
        ( 0,"Current Week", "Arrival Monitoring",  "#2D4A3E",
         "Confirm material has arrived at destination. "
         "Send all final documents including the <strong>final commercial invoice</strong>."),
        ( 1,"Week +1",      "Dispatch Closure",    "#B8924A",
         "Coordinate dispatch closure with customs agents. "
         "<em>If documentation is incomplete, shipments may be delayed with prior <strong>Sales Manager approval</strong>.</em>"),
        ( 2,"Week +2",      "Document Review",     "#4A6080",
         "Review draft documents with customs agents: AWB, phytosanitary certificate, "
         "commercial invoice, packing list, and certificate of origin."),
        ( 3,"Week +3",      "Advance Preview",     "#6B4080",
         "Verify special requirements: Colombia → certificate of origin; "
         "Brazil &amp; Costa Rica → import permit. Ask customers about last-minute additions."),
    ]

    week_dfs = [filter_week(df_all, *add_weeks(cur_year, cur_week, d)) for d,*_ in VIEWS]

    page_header(
        "Logistics Dashboard",
        f"ISO Week {cur_week}  ·  {today.strftime('%B %d, %Y')}  ·  Air Freight Operations"
    )

    tab_labels = ["Overview"] + [v[1] for v in VIEWS] + ["Future Shipments"]
    all_tabs   = st.tabs(tab_labels)

    # ── Overview ──────────────────────────────────────────────────────────────
    with all_tabs[0]:
        all_5w = pd.concat(week_dfs, ignore_index=True) if any(not d.empty for d in week_dfs) else pd.DataFrame()

        section_label("Five-Week Rolling Summary")
        n_s = n_shipments(all_5w) if not all_5w.empty else 0
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Shipments",     f"{n_s:,}")
        c2.metric("Product Lines", f"{len(all_5w):,}")
        c3.metric("Total Units",   f"{safe_int(all_5w['total_quantity'].sum() if not all_5w.empty else 0):,}")
        c4.metric("FOB Value",     f"$ {safe_float(all_5w['total_price'].sum() if not all_5w.empty else 0):,.0f}")
        c5.metric("Destinations",  f"{all_5w['country'].nunique() if not all_5w.empty else 0:,}")

        divider()
        section_label("Weekly Breakdown")
        ov_rows = []
        for i,(delta,wt,vt,accent,_) in enumerate(VIEWS):
            vy,vw = add_weeks(cur_year,cur_week,delta)
            wdf   = week_dfs[i]
            lbl   = "Past" if delta==-1 else ("Current" if delta==0 else f"+{delta}w")
            ov_rows.append({
                "Period":    f"{lbl}  ·  {week_label(vy,vw)}",
                "Stage":     vt,
                "Shipments": n_shipments(wdf) if not wdf.empty else 0,
                "Lines":     len(wdf),
                "Units":     f"{safe_int(wdf['total_quantity'].sum()):,}",
                "FOB":       f"$ {safe_float(wdf['total_price'].sum()):,.0f}",
                "Countries": wdf["country"].nunique() if not wdf.empty else 0,
            })
        st.dataframe(pd.DataFrame(ov_rows), use_container_width=True, hide_index=True)

        if not all_5w.empty:
            divider()
            section_label("Destination Breakdown  ·  All Active Weeks")
            dest = (
                all_5w.groupby(["country","iata_code"])
                .agg(ships=("shipment_id","nunique"), lines=("total_quantity","count"),
                     units=("total_quantity","sum"), fob=("total_price","sum"))
                .reset_index().sort_values(["country","fob"], ascending=[True,False])
            )
            dest["Country"] = dest["country"].apply(lambda c: f"{flag(c)}  {c}")
            dest = dest.rename(columns={"iata_code":"Airport","ships":"Shipments",
                                        "lines":"Lines","units":"Units","fob":"FOB (USD)"})
            dest["FOB (USD)"] = dest["FOB (USD)"].apply(lambda x: f"$ {x:,.0f}")
            dest["Units"]     = dest["Units"].apply(lambda x: f"{int(x):,}")
            st.dataframe(dest[["Country","Airport","Shipments","Lines","Units","FOB (USD)"]],
                         use_container_width=True, hide_index=True)

    # ── Week tabs ─────────────────────────────────────────────────────────────
    for tab,(delta,wt,vt,accent,msg),wdf in zip(all_tabs[1:-1],VIEWS,week_dfs):
        with tab:
            vy,vw = add_weeks(cur_year,cur_week,delta)
            n_s   = n_shipments(wdf) if not wdf.empty else 0

            section_label(f"{wt}  —  {vt}", accent)
            st.markdown(
                f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;'
                f'text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">'
                f'{week_label(vy,vw)}</div>', unsafe_allow_html=True)
            info_strip(msg, accent)

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Shipments",     f"{n_s:,}")
            c2.metric("Product Lines", f"{len(wdf):,}")
            c3.metric("Total Units",   f"{safe_int(wdf['total_quantity'].sum()):,}")
            c4.metric("FOB Value",     f"$ {safe_float(wdf['total_price'].sum()):,.0f}")
            c5.metric("Destinations",  f"{wdf['country'].nunique() if not wdf.empty else 0:,}")

            divider()
            section_label("Shipments by Destination", accent)
            render_by_destination(wdf, accent, dl_key=f"{delta}_{vw}_{vy}")

    # ── Future Shipments tab ──────────────────────────────────────────────────
    with all_tabs[-1]:
        # Anything beyond week +3
        cutoff_year, cutoff_week = add_weeks(cur_year, cur_week, 3)
        # Build a comparable date scalar for comparison
        import datetime as _dt
        cutoff_date = _dt.date.fromisocalendar(cutoff_year, cutoff_week, 7)  # end of W+3

        def row_date(r):
            try:
                return _dt.date.fromisocalendar(int(r["delivery_year"]), int(r["delivery_week"]), 1)
            except Exception:
                return _dt.date.min

        future_df = df_all[df_all.apply(lambda r: row_date(r) > cutoff_date, axis=1)].copy()

        section_label("Future Shipments  —  Beyond Week +3", "#6B4080")
        st.markdown(
            f'<div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.16em;'
            f'text-transform:uppercase;color:#7A7A7A;margin-bottom:14px;">'
            f'All confirmed orders after {week_label(cutoff_year, cutoff_week)}</div>',
            unsafe_allow_html=True)
        info_strip(
            "These are confirmed orders already in the system beyond the active logistics window. "
            "Review with the commercial team to ensure documentation preparation starts on time.",
            "#6B4080")

        if future_df.empty:
            st.info("No future shipments found beyond Week +3.")
        else:
            n_fut   = n_shipments(future_df)
            n_weeks = future_df["delivery_week"].nunique()
            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Shipments",     f"{n_fut:,}")
            c2.metric("Product Lines", f"{len(future_df):,}")
            c3.metric("Total Units",   f"{safe_int(future_df['total_quantity'].sum()):,}")
            c4.metric("FOB Value",     f"$ {safe_float(future_df['total_price'].sum()):,.0f}")
            c5.metric("Weeks Ahead",   f"{n_weeks:,}")

            divider()

            # Group by country → week → customer → shipment
            countries_fut = sorted(future_df["country"].unique())
            for country in countries_fut:
                cdf = future_df[future_df["country"]==country]
                tot_fob = safe_float(cdf["total_price"].sum())
                tot_shp = n_shipments(cdf)
                country_strip(country, tot_shp, tot_fob, "#6B4080")

                # Sort weeks ascending
                weeks_in_country = sorted(cdf[["delivery_year","delivery_week"]].drop_duplicates().values.tolist())
                for yw in weeks_in_country:
                    wy, ww = int(yw[0]), int(yw[1])
                    wdf_f = cdf[(cdf["delivery_year"]==wy) & (cdf["delivery_week"]==ww)]
                    n_sw  = n_shipments(wdf_f)
                    fob_w = safe_float(wdf_f["total_price"].sum())

                    with st.expander(
                        f"📅  {week_label(wy, ww)}   ·   {n_sw} shipment{'s' if n_sw!=1 else ''}  ·  $ {fob_w:,.0f} FOB",
                        expanded=False
                    ):
                        # Per shipment inside this country+week
                        for sid, sdf in wdf_f.groupby("shipment_id", sort=False):
                            customer = sdf["customer_name"].iloc[0]
                            origin   = sdf["supply_source_name"].iloc[0]
                            airport  = sdf["iata_code"].iloc[0]
                            shipment_row(
                                f"{customer}  ✈ {airport}", origin,
                                len(sdf),
                                safe_int(sdf["total_quantity"].sum()),
                                safe_float(sdf["total_price"].sum()),
                                "#6B4080"
                            )
                            line_cols = [c for c in ["crop_name","variety_name","product",
                                                     "total_quantity","total_price","order_type"]
                                         if c in sdf.columns]
                            ldf = sdf[line_cols].copy()
                            ldf.columns = [c.replace("_"," ").title() for c in ldf.columns]
                            if "Total Price"    in ldf.columns: ldf["Total Price"]    = ldf["Total Price"].apply(lambda x: f"$ {x:,.2f}")
                            if "Total Quantity" in ldf.columns: ldf["Total Quantity"] = ldf["Total Quantity"].apply(lambda x: f"{int(x):,}")
                            st.dataframe(ldf, use_container_width=True, hide_index=True)

            divider()
            # Full export
            buf = io.BytesIO()
            future_df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                "⬇  Export Future Shipments to Excel",
                data=buf.getvalue(),
                file_name="future_shipments.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_future"
            )


# ════════════════════════════════════════════════════════════════════════════
# AUTH — uses secrets.toml on Streamlit Cloud, plain comparison elsewhere
# ════════════════════════════════════════════════════════════════════════════
USERS_FILE = pathlib.Path(".streamlit/users.json")

# ── Hardcoded users dict — always works, no hashing at startup ───────────────
# Passwords stored as plain text here ONLY as a bootstrap fallback.
# Once you set secrets.toml these are ignored.
_BUILTIN_USERS = {
    "admin":      {"password": "admin123",   "display": "Administrator", "role": "admin"},
    "logistics":  {"password": "log2024",    "display": "Logistics",     "role": "user"},
    "commercial": {"password": "com2024",    "display": "Commercial",    "role": "user"},
}

def _get_users() -> dict:
    """
    Returns dict of {username: {password, display, role}}.
    Passwords are plain text — compared directly, no hashing required.
    Priority: secrets.toml → users.json → _BUILTIN_USERS
    """
    # 1 ── Streamlit secrets (Streamlit Cloud)
    try:
        raw = st.secrets.get("users", {})
        if raw:
            out = {}
            for u, v in raw.items():
                u = str(u).strip().lower()
                if isinstance(v, str):
                    out[u] = {"password": v, "display": u.title(), "role": "user"}
                else:
                    out[u] = {
                        "password": str(v.get("password", "")),
                        "display":  str(v.get("display",  u.title())),
                        "role":     str(v.get("role",     "user")),
                    }
            if out:
                return out
    except Exception:
        pass

    # 2 ── Local JSON file (self-hosted / local dev)
    if USERS_FILE.exists():
        try:
            data = json.loads(USERS_FILE.read_text())
            if data:
                return data
        except Exception:
            pass

    # 3 ── Built-in fallback (always works)
    return dict(_BUILTIN_USERS)

def _save_users(users: dict):
    try:
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        USERS_FILE.write_text(json.dumps(users, indent=2))
    except Exception:
        pass  # read-only on Streamlit Cloud — that's fine, secrets.toml is used there

def check_credentials(username: str, password: str) -> bool:
    if not username or not password:
        return False
    users = _get_users()
    u = username.strip().lower()
    if u not in users:
        return False
    stored = users[u].get("password", "")
    return stored == password.strip()

def get_user(username: str) -> dict:
    users = _get_users()
    return users.get(username.strip().lower(),
                     {"display": username.title(), "role": "user"})

# ── Login screen ──────────────────────────────────────────────────────────────
def render_login():
    components.html("""<style>
    html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],
    .main,.block-container{background-color:#F5F2ED!important;}
    </style>""", height=0)

    st.markdown("""
    <div style="text-align:center;padding:60px 0 32px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;
                  color:#1A1A1A;letter-spacing:.02em;">✦ Export Ops</div>
      <div style="font-family:'Jost',sans-serif;font-size:.65rem;letter-spacing:.22em;
                  text-transform:uppercase;color:#7A7A7A;margin-top:8px;">Management Suite</div>
    </div>""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("""
        <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;
                    padding:32px 32px 24px 32px;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:500;
                      color:#1A1A1A;">Sign in</div>
          <div style="font-family:'Jost',sans-serif;font-size:.78rem;color:#7A7A7A;
                      margin-top:4px;margin-bottom:20px;">
            Enter your credentials to continue
          </div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="username")
            password = st.text_input("Password", placeholder="••••••••", type="password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            if check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"]      = username.strip().lower()
                st.session_state["login_failed"]  = False
                st.rerun()
            else:
                st.session_state["login_failed"] = True

        if st.session_state.get("login_failed"):
            st.markdown("""
            <div style="background:#FFF5F5;border-left:3px solid #8C3D3D;padding:10px 14px;
                        font-family:'Jost',sans-serif;font-size:.78rem;color:#8C3D3D;
                        margin-top:8px;">
              Incorrect username or password.
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'Jost',sans-serif;font-size:.70rem;color:#9A9A9A;
                    text-align:center;margin-top:16px;padding-bottom:8px;">
          Access restricted to authorised personnel.
        </div>""", unsafe_allow_html=True)

# ── Admin panel ───────────────────────────────────────────────────────────────
def render_admin():
    page_header("User Management", "Add · Edit · Remove Users")
    users = _get_users()

    section_label("Current Users", "#8C3D3D")
    rows = [{"Username": u, "Display Name": v["display"], "Role": v["role"]}
            for u, v in users.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    divider()

    section_label("Add or Update User", "#2D4A3E")
    c1, c2, c3, c4 = st.columns(4)
    new_user    = c1.text_input("Username",     key="adm_user",    placeholder="e.g. maria")
    new_display = c2.text_input("Display Name", key="adm_display", placeholder="e.g. María")
    new_pw      = c3.text_input("Password",     key="adm_pw",      type="password", placeholder="Password")
    new_role    = c4.selectbox("Role",          ["user", "admin"],  key="adm_role")
    if st.button("Save User", key="adm_save"):
        u = new_user.strip().lower()
        if not u:
            st.warning("Username cannot be empty.")
        elif not new_pw and u not in users:
            st.warning("Password required for new users.")
        else:
            users[u] = {
                "password": new_pw if new_pw else users.get(u, {}).get("password", ""),
                "display":  new_display.strip() or u.title(),
                "role":     new_role,
            }
            _save_users(users)
            st.success(f"User **{u}** saved.")
            st.rerun()
    divider()

    section_label("Remove User", "#B8924A")
    removable = [u for u in users if u != st.session_state.get("username")]
    if removable:
        del_user = st.selectbox("Select user to remove", removable, key="adm_del")
        if st.button("Remove User", key="adm_del_btn"):
            del users[del_user]
            _save_users(users)
            st.success(f"User **{del_user}** removed.")
            st.rerun()
    else:
        st.info("No other users to remove.")
    divider()

    section_label("Change My Password", "#4A6080")
    cp1, cp2 = st.columns(2)
    cur_pw  = cp1.text_input("Current password", type="password", key="cp_cur")
    new_pw2 = cp2.text_input("New password",     type="password", key="cp_new")
    if st.button("Update Password", key="cp_btn"):
        me = st.session_state.get("username", "")
        if not check_credentials(me, cur_pw):
            st.error("Current password is incorrect.")
        elif len(new_pw2) < 6:
            st.warning("Password must be at least 6 characters.")
        else:
            users[me]["password"] = new_pw2
            _save_users(users)
            st.success("Password updated.")

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated", False):
    render_login()
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    current_user = get_user(st.session_state.get("username", ""))
    display_name = current_user["display"]
    is_admin     = current_user["role"] == "admin"

    st.markdown(f"""
    <div style="padding:32px 0 6px 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:400;
                  color:#F5EDE8;letter-spacing:.04em;line-height:1.2;">✦ Export Ops</div>
      <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                  text-transform:uppercase;color:#C4A090;margin-top:4px;">Management Suite</div>
    </div>
    <div style="border-top:1px solid rgba(212,176,168,.25);margin:14px 0 10px 0;"></div>
    <div style="font-family:Jost,sans-serif;font-size:.74rem;color:#D4B8B0;padding-bottom:14px;">
      <span style="color:#C4A090;font-size:.60rem;letter-spacing:.12em;text-transform:uppercase;">Signed in as</span><br>
      <span style="color:#F5EDE8;font-weight:500;">{display_name}</span>
    </div>
    <div style="border-top:1px solid rgba(212,176,168,.25);margin:0 0 16px 0;"></div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Navigation</p>', unsafe_allow_html=True)

    nav_options = ["📦  Logistics", "📈  Commercial Intelligence"]
    if is_admin:
        nav_options.append("👤  User Management")

    page = st.radio("page_nav", nav_options,
                    label_visibility="collapsed", key="page_selector")

    st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:20px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Data Source</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Excel file", type=["xlsx","xls"], label_visibility="collapsed")

    if "df" in st.session_state and st.session_state.df is not None:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.07);border:1px solid rgba(212,176,168,.2);
                    padding:12px 14px;margin-top:10px;font-family:Jost,sans-serif;
                    font-size:.74rem;line-height:2;">
          <span style="color:#D4B070;">●</span>
          <span style="color:#F5EDE8;margin-left:6px;">{st.session_state.filename}</span><br>
          <span style="color:#C4A090;">Updated&nbsp;&nbsp;</span>
          <span style="color:#F5EDE8;">{st.session_state.loaded_at}</span><br>
          <span style="color:#C4A090;">Records&nbsp;&nbsp;&nbsp;</span>
          <span style="color:#F5EDE8;">{len(st.session_state.df):,}</span>
        </div>""", unsafe_allow_html=True)

        if page == "📦  Logistics":
            st.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:20px 0;"></div>', unsafe_allow_html=True)
            st.markdown('<p style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;color:#C4A090;margin-bottom:8px;">Filters</p>', unsafe_allow_html=True)
            origins   = st.multiselect("Origin",   sorted(st.session_state.df["supply_source_name"].dropna().unique()), placeholder="All origins",   key="log_origins")
            customers = st.multiselect("Customer", sorted(st.session_state.df["customer_name"].dropna().unique()),       placeholder="All customers", key="log_customers")
            st.session_state.origins   = origins
            st.session_state.customers = customers

    # Sign out
    st.sidebar.markdown('<div style="border-top:1px solid rgba(212,176,168,.25);margin:24px 0 12px 0;"></div>', unsafe_allow_html=True)
    if st.sidebar.button("Sign Out", key="signout_btn"):
        for k in ["authenticated","username","login_failed","df","filename",
                  "loaded_at","origins","customers"]:
            st.session_state.pop(k, None)
        st.rerun()


# ── File processing ───────────────────────────────────────────────────────────
if uploaded is not None:
    df_new, err = load_and_validate(uploaded)
    if err:
        st.error(f"⚠️ {err}")
        st.stop()
    st.session_state.df        = df_new
    st.session_state.filename  = uploaded.name
    st.session_state.loaded_at = datetime.now().strftime("%b %d, %Y  %H:%M")
    if "origins"   not in st.session_state: st.session_state.origins   = []
    if "customers" not in st.session_state: st.session_state.customers = []


# ── Welcome screen ────────────────────────────────────────────────────────────
if "df" not in st.session_state or st.session_state.df is None:
    st.markdown("""
    <div style="max-width:640px;margin:100px auto 0 auto;padding:0 24px;">

      <div style="font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:300;
                  color:#1A1A1A;letter-spacing:.01em;line-height:1.15;text-align:center;
                  margin-bottom:6px;">
        Export Operations Suite
      </div>

      <div style="font-family:Jost,sans-serif;font-size:.68rem;letter-spacing:.22em;
                  text-transform:uppercase;color:#7A7A7A;text-align:center;margin-bottom:48px;">
        Fresh Flowers &amp; Vegetables &nbsp;·&nbsp; Air Freight
      </div>

      <div style="border-top:1px solid #DDD8D0;border-bottom:1px solid #DDD8D0;
                  padding:36px 0;margin-bottom:36px;text-align:center;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-style:italic;
                    color:#7A7A7A;margin-bottom:16px;">
          Upload your weekly Excel file to begin
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;
                    line-height:1.9;">
          Use the <strong style="color:#8C3D3D;">sidebar uploader</strong> on the left.<br>
          Switch between <strong>Logistics</strong> and <strong>Commercial Intelligence</strong> using the navigation menu.
        </div>
      </div>

      <div style="background:#FFFFFF;border:1px solid #DDD8D0;border-top:3px solid #8C3D3D;
                  padding:28px 32px;">
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                    text-transform:uppercase;color:#8C3D3D;margin-bottom:14px;">
          Required columns
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#4A4A4A;line-height:2.1;">
          delivery_year &nbsp;·&nbsp; delivery_week &nbsp;·&nbsp; customer_name<br>
          supply_source_name &nbsp;·&nbsp; destination &nbsp;·&nbsp; total_quantity &nbsp;·&nbsp; total_price
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.62rem;letter-spacing:.2em;
                    text-transform:uppercase;color:#7A7A7A;margin:20px 0 10px 0;">
          Optional columns
        </div>
        <div style="font-family:Jost,sans-serif;font-size:.84rem;color:#7A7A7A;line-height:2.1;">
          secondary_customer_name &nbsp;·&nbsp; crop_name &nbsp;·&nbsp; variety_name<br>
          order_type &nbsp;·&nbsp; product
        </div>
      </div>

    </div>""", unsafe_allow_html=True)
    st.stop()


# ── Routing ───────────────────────────────────────────────────────────────────
if page == "📈  Commercial Intelligence":
    render_commercial(st.session_state.df.copy() if "df" in st.session_state and st.session_state.df is not None else pd.DataFrame())
elif page == "👤  User Management":
    if is_admin:
        render_admin()
    else:
        st.error("Access denied.")
else:
    df_log = apply_filters(
        st.session_state.df.copy() if "df" in st.session_state and st.session_state.df is not None else pd.DataFrame(),
        st.session_state.get("origins", []),
        st.session_state.get("customers", [])
    )
    render_logistics(df_log)
